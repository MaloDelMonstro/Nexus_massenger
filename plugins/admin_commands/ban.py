from plugins import BasePlugin, PluginContext, PluginResponse
from datetime import datetime, timezone

from extensions import db, socketio
from models import User


class BanPlugin(BasePlugin):
    name = "ban"
    description = "Заблокировать или разблокировать пользователя"
    version = "1.0.0"
    required_role = "admin"
    author = "Nexus team"

    commands = {
        "//ban": "Заблокировать пользователя: //ban <username|id> [причина]",
        "//unban": "Разблокировать пользователя: //unban <username|id>"
    }

    def execute(self, command: str, args: list[str], ctx: PluginContext) -> PluginResponse:
        if not args:
            return PluginResponse.error("Укажите пользователя: //ban <username|id> <причина>")

        target_identifier = args[0]
        ban_reason = " ".join(args[1:]) if len(args) > 1 else "Нарушение правил"

        try:
            user = self._find_user(target_identifier)
            if not user:
                return PluginResponse.error(f"Пользователь {target_identifier} не найден.")

            if user.id == ctx.user_id:
                return PluginResponse.error("Нельзя заблокировать самого себя.")

            if command in ['ban', '//ban']:
                return self._handle_ban(user, ban_reason, ctx)
            elif command in ['unban', '//unban']:
                return self._handle_unban(user, ctx)
            else:
                return PluginResponse.error("Неизвестная команда.")

        except Exception as e:
            db.session.rollback()
            return PluginResponse.error(f"{str(e)}")

    def _handle_ban(self, user: User, reason: str, ctx: PluginContext) -> PluginResponse:
        if user.is_banned:
            return PluginResponse.error(f"Пользователь {user.username} уже заблокирован.")

        user.is_banned = True
        user.ban_reason = reason
        user.ban_until = datetime.now(timezone.utc)
        user.admin_notes = f"[{datetime.now().strftime('%d.%m.%Y')}] Забанен: {reason}\n" + (user.admin_notes or "")
        user.admin_notes_updated = datetime.now(timezone.utc)

        db.session.commit()

        socketio.emit('user_banned', {
            'user_id': user.id,
            'username': user.username,
            'reason': reason,
            'banned_by': ctx.user_id
        })

        self._log_action(ctx.user_id, 'ban', user.id, reason)

        return PluginResponse.ok(
            f"Пользователь {user.username} заблокирован.\n"
            f"Причина: {reason}"
        )

    def _handle_unban(self, user: User, ctx: PluginContext) -> PluginResponse:
        if not user.is_banned:
            return PluginResponse.error(f"Пользователь {user.username} не заблокирован.")

        user.is_banned = False
        user.ban_reason = None
        user.ban_until = None

        db.session.commit()

        socketio.emit('user_unbanned', {
            'user_id': user.id,
            'username': user.username,
            'unbanned_by': ctx.user_id
        })

        self._log_action(ctx.user_id, 'unban', user.id)

        return PluginResponse.ok(f"Пользователь {user.username} разблокирован.")

    @staticmethod
    def _find_user(identifier: str) -> User | None:
        if identifier.isdigit():
            return User.query.get(int(identifier))

        user = User.query.filter_by(username=identifier).first()
        if user:
            return user

        user = User.query.filter(User.username.ilike(f"%{identifier}%")).first()
        return user


    @staticmethod
    def _log_action(admin_id: int, action: str, target_id: int, reason: str = None):
        log_entry = (
            f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] "
            f"Admin {admin_id} performed {action} on user {target_id}"
        )
        if reason:
            log_entry += f" (reason: {reason})"

    @staticmethod
    def help() -> str:
        return (
            "Бан/Разбан пользователей\n"
            "\n"
            "//ban <username|id> <причина>  — Заблокировать пользователя\n"
            "//unban <username|id>           — Разблокировать пользователя\n"
            "\n"
            "Примеры:\n"
            "  //ban spammer123 Рассылка спама\n"
            "  //ban 52\n"
            "  //unban spammer123"
        )