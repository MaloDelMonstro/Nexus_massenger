from plugins.base import BasePlugin, PluginContext, PluginResponse


class HelpPlugin(BasePlugin):
    name = "help"
    description = "Справка"
    commands = {'help': 'Показать команды'}

    def execute(self, command: str, args: list[str], ctx: PluginContext) -> PluginResponse:
        return PluginResponse.ok("Плагин работает! Введите /roll для теста.")