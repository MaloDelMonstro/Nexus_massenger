from plugins import BasePlugin, PluginContext, PluginResponse
from extensions import db
from models import User
from datetime import datetime, timezone, timedelta
import secrets


class GetAPIPlugin(BasePlugin):
    name = "getapi"
    description = "Получить API ключ для интеграции"
    version = "1.0.0"
    cooldown = 300
    author = "Nexus team"

    commands = {
        'api': 'Короткая команда',
        'getapi': 'Получить API ключ',
    }

    def execute(self, command: str, args: list[str], ctx: PluginContext) -> PluginResponse:
        try:
            user = User.query.get(ctx.user_id)
            if not user:
                return PluginResponse.error("Пользователь не найден")

            if hasattr(user, 'api_key_generated_at') and user.api_key_generated_at:
                time_since_last = datetime.now(timezone.utc) - user.api_key_generated_at
                if time_since_last < timedelta(seconds=self.cooldown):
                    remaining = int(self.cooldown - time_since_last.total_seconds())
                    return PluginResponse.error(
                        f"Подождите {remaining} сек. перед повторной генерацией"
                    )

            api_key = f"nexus_{secrets.token_hex(32)}"

            user.api_key = api_key

            user.api_key_generated_at = datetime.now(timezone.utc)

            db.session.commit()

            message = (
                f"API ключ создан!\n\n"
                f"Ключ:\n"
                f"\n{api_key}\n\n\n"
                f"Важно:\n"
                f"• Сохраните ключ в безопасном месте\n"
                f"• Он не будет показан повторно\n"
                f"• Не передавайте третьим лицам\n\n"
                f"Использование:\n"
                f"POST /api/v1/plugins/execute\n"
                f"Headers:\n"
                f"  X-API-Key: {api_key}\n"
                f"  Content-Type: application/json\n\n"
                f"Body:\n"
                f'{{"command": "roll", "args": ["100"]}}\n'
                f"\n\n"
                f"Документация:\n"
                f"• Список плагинов: /api/v1/plugins/list\n"
                f"• Справка: /api/v1/plugins/help?plugin=name\n"
                f"• Ваш профиль: /api/v1/me"
            )

            if user.is_admin:
                message += (
                    f"\n\nАдминистративный доступ:\n"
                    f"Ваш ключ имеет доступ к админским командам:\n"
                    f"/ban, /unban — управление пользователями\n"
                    f"/admin, /deadmin — управление правами"
                )

            print(f"API ключ создан для {user.username} (ID: {user.id})")

            return PluginResponse.ok(message)

        except Exception as e:
            db.session.rollback()

            return PluginResponse.error(f"Ошибка создания ключа: {e}")

    @staticmethod
    def help() -> str:
        return (
            "Получение API ключа\n\n"
            "API ключ позволяет управлять аккаунтом и "
            "выполнять команды через внешние приложения.\n\n"
            "/api              — Короткая команда\n"
            "/getapi           — Альтернативная команда\n"
            "\n\n"
            "Возможности:\n"
            "• Выполнение команд плагинов\n"
            "• Получение списка плагинов\n"
            "• Доступ к справке\n"
            "• Просмотр профиля\n\n"
            "Безопасность:\n"
            "• Ключ показывается только один раз\n"
            "• Храните в секрете\n"
            "• Можно сгенерировать заново через 5 минут\n\n"
            "Кулдаун: 300 секунд (5 минут)\n\n"
        )