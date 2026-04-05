import importlib
import pkgutil
from pathlib import Path
from .base import BasePlugin, PluginContext, PluginResponse
from .registry import CommandRegistry


class PluginManager:
    def __init__(self, plugins_dir: str = "plugins"):
        self.plugins_dir = Path(plugins_dir)
        self.plugins: dict[str, BasePlugin] = {}
        self.registry = CommandRegistry()
        self._loaded_modules: list[str] = []

    def load_all(self) -> list[str]:
        loaded = []
        print("Начинаю загрузку плагинов...")

        commands_path = self.plugins_dir / "commands"
        if commands_path.exists():
            print(f"Сканирую {commands_path}")
            for module_info in pkgutil.iter_modules([str(commands_path)]):
                if module_info.name.startswith('_'):
                    continue
                try:
                    print(f"   Загрузка: commands.{module_info.name}")
                    module = importlib.import_module(f"plugins.commands.{module_info.name}")
                    self._register_plugin_module(module)
                    loaded.append(f"commands.{module_info.name}")
                    self._loaded_modules.append(module_info.name)
                    print(f"   Успешно: {module_info.name}")
                except Exception as e:
                    print(f"   Ошибка {module_info.name}: {e}")
                    import traceback
                    traceback.print_exc()

        print(f"\nВсего загружено: {len(loaded)}")
        print(f"Зарегистрировано команд: {len(self.registry.commands)}")
        for cmd in self.registry.commands:
            print(f"   /{cmd}")

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
                    self.registry.register(command, plugin)
                    print(f"      ↳ Зарегистрирована команда: /{command}")

    def execute_command(self, full_command: str, ctx: PluginContext) -> PluginResponse | None:
        if not full_command.startswith('/'):
            return None

        parts = full_command[1:].strip().split(maxsplit=1)
        command = parts[0].lower()
        args = parts[1].split() if len(parts) > 1 else []

        print(f"Выполнение команды: /{command} {args}")

        plugin = self.registry.get_plugin(command)
        if not plugin:
            print(f"   Команда не найдена: {command}")
            return PluginResponse.error(f"Команда /{command} не найдена")

        print(f"   Найдено плагин: {plugin.name}")

        can_run, error_msg = plugin.can_execute(ctx)
        if not can_run:
            return PluginResponse.error(error_msg)

        try:
            response = plugin.execute(command, args, ctx)
            plugin.record_usage(ctx)
            print(f"   ✓ Выполнено: {response.message[:50]}...")
            return response
        except Exception as e:
            print(f"   Ошибка: {e}")
            import traceback
            traceback.print_exc()
            return PluginResponse.error(f"Ошибка: {type(e).__name__}")