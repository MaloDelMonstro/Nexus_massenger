from plugins.base import BasePlugin, PluginContext, PluginResponse
import random


class RollPlugin(BasePlugin):
    name = "roll"
    description = "Бросок кубика"
    commands = {'roll': 'Бросить кубик'}

    def execute(self, command: str, args: list[str], ctx: PluginContext) -> PluginResponse:
        max_val = int(args[0]) if args else 100
        result = random.randint(1, max_val)
        return PluginResponse.ok(f"Выпало: {result} из {max_val}")