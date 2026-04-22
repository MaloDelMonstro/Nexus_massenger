import importlib
import pkgutil
from pathlib import Path
from plugins.base import BasePlugin, PluginContext, PluginResponse
from plugins.base.registry import CommandRegistry


class PluginManager:
    def __init__(self, plugins_dir: str = "plugins"):
        self.plugins_dir = Path(plugins_dir)
        self.plugins: dict[str, BasePlugin] = {}
        self.registry = CommandRegistry()
        self._loaded_modules: list[str] = []

    def load_all(self) -> list[str]:
        loaded = []

        commands_path = self.plugins_dir / "commands"
        if commands_path.exists():
            for module_info in pkgutil.iter_modules([str(commands_path)]):
                if module_info.name.startswith('_'):
                    continue
                try:
                    module = importlib.import_module(f"plugins.commands.{module_info.name}")
                    self._register_plugin_module(module)
                    loaded.append(f"commands.{module_info.name}")
                    self._loaded_modules.append(module_info.name)
                except Exception as e:
                    print(f"Ошибка {module_info.name}: {e}")
                    import traceback
                    traceback.print_exc()

        admin_path = self.plugins_dir / "admin_commands"
        if admin_path.exists():
            for module_info in pkgutil.iter_modules([str(admin_path)]):
                if module_info.name.startswith('_'):
                    continue
                try:
                    module = importlib.import_module(f"plugins.admin_commands.{module_info.name}")
                    self._register_plugin_module(module)
                    loaded.append(f"admin_commands.{module_info.name}")
                    self._loaded_modules.append(module_info.name)
                except Exception as e:
                    print(f"{e}")

        # for cmd in sorted(self.registry.commands.keys()):
        #     print(f"   /{cmd}")

        return loaded

    def _register_plugin_module(self, module):
        for attr_name in dir(module):
            attr = getattr(module, attr_name)
            if (isinstance(attr, type) and
                    issubclass(attr, BasePlugin) and
                    attr != BasePlugin and
                    attr.name):

                plugin = attr()
                self.plugins[plugin.name.lower()] = plugin

                for command in plugin.commands:
                    cmd_key = command.strip('/')
                    self.registry.register(cmd_key, plugin)

    def execute_command(self, full_command: str, ctx: PluginContext) -> PluginResponse | None:
        if not full_command.startswith('/'):
            return None

        cmd_text = full_command.lstrip('/')

        if not cmd_text:
            return None

        parts = cmd_text.strip().split(maxsplit=1)
        command = parts[0].lower()
        args = parts[1].split() if len(parts) > 1 else []

        plugin = self.registry.get_plugin(command)
        if not plugin:
            return PluginResponse.error(f"Команда /{full_command.lstrip('/')} не найдена")

        can_run, error_msg = plugin.can_execute(ctx)
        if not can_run:
            return PluginResponse.error(f"{error_msg}")

        try:
            response = plugin.execute(command, args, ctx)
            plugin.record_usage(ctx)
            return response
        except Exception as e:
            return PluginResponse.error(f"{e}")