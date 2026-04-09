from plugins.base import BasePlugin, PluginContext, PluginResponse
from flask import current_app


class HelpPlugin(BasePlugin):
    name = "help"
    description = "Полный список всех доступных команд"
    version = "1.1.0"
    commands = {'help': 'Показать все зарегистрированные команды'}

    def execute(self, command: str, args: list[str], ctx: PluginContext) -> PluginResponse:
        try:
            manager = current_app.extensions.get('plugin_manager')
            if not manager or not hasattr(manager, 'registry'):
                return PluginResponse.error("Система плагинов не инициализирована")

            registry = manager.registry.commands
            if not registry:
                return PluginResponse.ok("Пока нет доступных команд.")

            visible_commands = []
            added = set()

            for cmd, plugin in sorted(registry.items()):
                if cmd not in added:
                    desc = plugin.commands.get(cmd, "Без описания")
                    visible_commands.append(f"/{cmd} — {desc}")
                    added.add(cmd)

            if not visible_commands:
                return PluginResponse.ok("Команды не найдены.")

            help_msg = "Все доступные команды:\n\n"
            help_msg += "\n".join(visible_commands)
            help_msg += f"\n\nВсего: {len(visible_commands)}"

            return PluginResponse.ok(help_msg)

        except Exception as e:
            return PluginResponse.error(f"Ошибка {str(e)}")