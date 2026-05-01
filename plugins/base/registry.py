from .base import BasePlugin


class CommandRegistry:
    def __init__(self):
        self.commands: dict[str, BasePlugin] = {}

    def register(self, command: str, plugin: BasePlugin) -> None:
        self.commands[command.lower().strip('/')] = plugin

    def get_plugin(self, command: str) -> BasePlugin | None:
        return self.commands.get(command.lower().strip('/'))

    def list_commands(self) -> list[str]:
        return list(self.commands.keys())
