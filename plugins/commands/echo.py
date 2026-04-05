from plugins.base import BasePlugin, PluginContext, PluginResponse
from plugins.security import SecurityPolicy


class EchoPlugin(BasePlugin):
    name = "echo"
    description = "Повторяет ваш текст (тестовый плагин)"
    version = "1.0.0"
    cooldown = 5

    commands = {
        'echo': 'Повторить текст: /echo <ваш текст>'
    }

    async def execute(self, command: str, args: list[str], ctx: PluginContext) -> PluginResponse:
        if not args:
            return PluginResponse.error("Укажите текст: `/echo привет`")

        text = ' '.join(args)
        sanitized = SecurityPolicy.sanitize_arg(text)

        return PluginResponse.ok(f"🔊 {sanitized}", ephemeral=False)