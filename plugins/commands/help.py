from plugins.base import BasePlugin, PluginContext, PluginResponse
from flask import current_app


class HelpPlugin(BasePlugin):
    name = "help"
    description = "Справка по командам и плагинам"
    version = "2.0"
    commands = {'help': 'Список команд или инфо: /help [команда]'}
    author = "Nexus team"

    def execute(self, command: str, args: list[str], ctx: PluginContext) -> PluginResponse:
        try:
            manager = current_app.extensions.get('plugin_manager')
            if not manager or not hasattr(manager, 'registry'):
                return PluginResponse.error("Система плагинов не инициализирована")

            registry = manager.registry.commands
            plugins = manager.plugins

            if args:
                query = args[0].lower().strip('/')

                plugin = registry.get(query)

                if not plugin:
                    plugin = plugins.get(query)

                if plugin:
                    cmd_list = []
                    for cmd, desc in plugin.commands.items():
                        cmd_list.append(f"  /{cmd} — {desc}")

                    info_text = f"{plugin.name} v{plugin.version}\n"

                    if plugin.author and plugin.author != "Unknown":
                        info_text += f"Автор: {plugin.author}\n"

                    info_text += f"Описание: {plugin.description}\n\n"
                    info_text += "Доступные команды:\n" + "\n".join(cmd_list)

                    if hasattr(plugin, 'cooldown') and plugin.cooldown > 0:
                        info_text += f"\nКулдаун: {plugin.cooldown} сек."

                    return PluginResponse.ok(info_text)
                else:
                    return PluginResponse.error(f"Команда или плагин {query} не найдена")

            visible_commands = []
            added = set()

            for cmd, plugin in sorted(registry.items()):
                if cmd not in added:
                    desc = plugin.commands.get(cmd, "Без описания")
                    visible_commands.append(f"/{cmd} — {desc}")
                    added.add(cmd)

            if not visible_commands:
                return PluginResponse.ok("Пока нет доступных команд.")

            help_msg = "Все доступные команды:\n\n"
            help_msg += "\n".join(visible_commands)
            help_msg += f"\n\nИспользуйте /help <команда> для подробной информации"

            return PluginResponse.ok(help_msg)

        except Exception as e:
            return PluginResponse.error(f"Ошибка справки: {type(e).__name__}")