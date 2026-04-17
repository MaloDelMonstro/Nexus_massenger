from plugins import BasePlugin, PluginContext, PluginResponse
import random


class RandomPlugin(BasePlugin):

    name = "roll"
    description = "Бросить кубик (случайное число)"
    version = "1.1"
    commands = {
        'random': 'Случайное число: /random [макс.число]'
    }
    author = "Nexus team"
    cooldown = 2

    def execute(self, command: str, args: list[str], ctx: PluginContext) -> PluginResponse:
        try:
            max_val = int(args[0]) if args else 100

            if max_val < 1:
                return PluginResponse.error("Максимальное число должно быть больше 0")

            if max_val > 1000000:
                return PluginResponse.error("Максимальное число не может превышать 1,000,000")

            result = random.randint(1, max_val)
            return PluginResponse.ok(f"Выпало: {result} из {max_val}")

        except ValueError:
            return PluginResponse.error("Укажите корректное число")
        except Exception as e:
            return PluginResponse.error(f"Ошибка: {type(e).__name__}")

    @staticmethod
    def help() -> str:
        return (
            "Рандомное число\n\n"
            "\n"
            "/roll [число]     — Бросить кубик (по умолчанию 100)\n"
            "/random [число]   — Случайное число от 1 до N\n"
            "\n\n"
            "Примеры:\n"
            "  /random 1000 — число от 1 до 1000\n\n"
            "Кулдаун: 2 секунды"
        )