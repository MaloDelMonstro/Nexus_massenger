from plugins.base import BasePlugin, PluginContext, PluginResponse


class EchoPlugin(BasePlugin):
    name = "echo"
    description = "Повторяет сообщение указанное количество раз"
    version = "1.0.0"

    commands = {
        'echo': 'Повторить текст: /echo <сообщение> [кол-во]'
    }

    def execute(self, command: str, args: list[str], ctx: PluginContext) -> PluginResponse:
        if not args:
            return PluginResponse.error("Используйте: `/echo <текст> [кол-во]`")

        count = 1
        message_parts = args

        try:
            potential_count = int(args[-1])
            if 1 <= potential_count <= 10:
                count = potential_count
                message_parts = args[:-1]
            elif potential_count > 10:
                return PluginResponse.error("Максимум 10 повторений (защита от спама)")
            else:
                return PluginResponse.error("Количество повторений должно быть больше 0")
        except (ValueError, IndexError):
            pass

        if not message_parts:
            return PluginResponse.error("Укажите текст для повтора")

        message = " ".join(message_parts)
        result = "\n".join([message] * count)

        return PluginResponse.ok(result)