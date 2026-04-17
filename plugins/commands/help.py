from plugins import BasePlugin, PluginContext, PluginResponse
from flask import current_app


class HelpPlugin(BasePlugin):
    name = "help"
    description = "Справка по командам и плагинам"
    version = "3.0"
    commands = {
        'help': 'Список команд или инфо: /help [команда]',
        '//help': 'Справка для админов: //help [команда]'
    }
    author = "Nexus team"
    cooldown = 3

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
                    if hasattr(plugin, 'help') and callable(plugin.help):
                        detailed_info = plugin.help()
                        return PluginResponse.ok(detailed_info)

                    return self._get_plugin_info(plugin)
                else:
                    return PluginResponse.error(f"Команда или плагин {query} не найдены")

            return self._get_all_commands(registry, ctx)

        except Exception as e:
            print(f"HelpPlugin error: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()
            return PluginResponse.error(f"Ошибка справки: {type(e).__name__}")

    @staticmethod
    def _get_plugin_info(plugin: BasePlugin) -> PluginResponse:
        cmd_list = []
        for cmd, desc in plugin.commands.items():
            cmd_list.append(f"  `/{cmd}` — {desc}")

        info_text = f"{plugin.name} v{plugin.version}\n\n"

        if plugin.author and plugin.author != "Unknown":
            info_text += f"Автор: {plugin.author}\n"

        info_text += f"Описание: {plugin.description}\n\n"

        if cmd_list:
            info_text += "Команды:\n" + "\n".join(cmd_list)

        if hasattr(plugin, 'cooldown') and plugin.cooldown > 0:
            info_text += f"\n\nКулдаун: {plugin.cooldown} сек."

        if hasattr(plugin, 'required_role') and plugin.required_role:
            role_name = "Администратор" if plugin.required_role == "admin" else plugin.required_role
            info_text += f"\nТребуется роль: {role_name}"

        return PluginResponse.ok(info_text)

    @staticmethod
    def _get_all_commands(registry: dict, ctx: PluginContext) -> PluginResponse:
        visible_commands = []
        added = set()

        admin_commands = []
        user_commands = []
        other_commands = []

        for cmd, plugin in sorted(registry.items()):
            if cmd in added:
                continue

            if hasattr(plugin, 'required_role') and plugin.required_role == 'admin':
                if not ctx.user_is_admin:
                    continue
                admin_commands.append((cmd, plugin))
            else:
                user_commands.append((cmd, plugin))

            added.add(cmd)

        help_msg = "Справка по командам\n\n"

        if user_commands:
            help_msg += "Пользовательские:\n"
            for cmd, plugin in user_commands:
                desc = plugin.commands.get(cmd, "Без описания")
                help_msg += f"  /{cmd} — {desc}\n"
            help_msg += "\n"

        if admin_commands and ctx.user_is_admin:
            help_msg += "Административные:\n"
            for cmd, plugin in admin_commands:
                desc = plugin.commands.get(cmd, "Без описания")
                help_msg += f"  /{cmd} — {desc}\n"
            help_msg += "\n"

        if not user_commands and not admin_commands:
            return PluginResponse.ok("Пока нет доступных команд.")

        help_msg += "Используйте /help <команда> для подробной информации"

        return PluginResponse.ok(help_msg)

    @staticmethod
    def help() -> str:
        return (
            "Справка по плагинам\n\n"
            "\n"
            "/help              — Показать все доступные команды\n"
            "/help <команда>    — Подробная информация о команде\n"
            "\n\n"
            "Примеры:\n"
            "  /help — список всех команд\n"
            "  /help ban — информация о бане\n"
            "  /help help — эта справка\n\n"
            "Команды администраторов скрыты от обычных пользователей."
        )