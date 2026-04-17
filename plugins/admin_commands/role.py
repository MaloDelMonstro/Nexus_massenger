from plugins.base import BasePlugin, PluginContext, PluginResponse, SecurityPolicy
from datetime import datetime, timezone

from extensions import db, socketio
from models import User


class RolePlugin(BasePlugin):
    name = "role"
    description = "Назначить или снять роль администратора"
    version = "1.0.0"
    required_role = "admin"
    cooldown = 10
    author = "Nexus team"

    commands = {
        "//admin": "Назначить администратора: //admin <username|id>",
        "//deadmin": "Снять роль администратора: //deadmin <username|id>"
    }

    def execute(self, command: str, args: list[str], ctx: PluginContext) -> PluginResponse:
        is_safe, error_msg = SecurityPolicy.validate_command(command, args, ctx.user_is_admin)
        if not is_safe:
            return PluginResponse.error(f"{error_msg}")

        if not args:
            return PluginResponse.error(
                "Укажите пользователя: //admin <username|id>"
            )

        target_identifier = SecurityPolicy.sanitize_arg(args[0])

        try:
            user = self._find_user(target_identifier)
            if not user:
                return PluginResponse.error(f"Пользователь {target_identifier} не найден.")

            if user.id == ctx.user_id:
                return PluginResponse.error("Нельзя изменить свои собственные права.")

            if command == "//admin":
                return self._handle_promote(user, ctx)
            elif command == "//deadmin":
                return self._handle_demote(user, ctx)
            else:
                return PluginResponse.error("Неизвестная команда.")

        except Exception as e:
            db.session.rollback()
            print(f"RolePlugin error: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()
            return PluginResponse.error(f"Ошибка сервера: {str(e)}")

    def _handle_promote(self, user: User, ctx: PluginContext) -> PluginResponse:
        if user.is_admin:
            return PluginResponse.error(f"Пользователь {user.username} уже является администратором.")

        user.is_admin = True
        user.admin_notes = f"[{datetime.now().strftime('%d.%m.%Y %H:%M')}] Назначен админом от {ctx.username}\n" + (
                    user.admin_notes or "")
        user.admin_notes_updated = datetime.now(timezone.utc)

        db.session.commit()

        socketio.emit('user_role_changed', {
            'user_id': user.id,
            'username': user.username,
            'new_role': 'admin',
            'changed_by': ctx.username,
            'action': 'promote'
        }, broadcast=True)

        self._log_action(ctx.user_id, 'promote', user.id)

        return PluginResponse.ok(
            f"Пользователь {user.username} назначен администратором.\n"
            f"Права выдал: {ctx.username}"
        )

    def _handle_demote(self, user: User, ctx: PluginContext) -> PluginResponse:
        if not user.is_admin:
            return PluginResponse.error(f"Пользователь {user.username} не является администратором.")

        user.is_admin = False
        user.admin_notes = f"[{datetime.now().strftime('%d.%m.%Y %H:%M')}] Снят с должности админа от {ctx.username}\n" + (
                    user.admin_notes or "")
        user.admin_notes_updated = datetime.now(timezone.utc)

        db.session.commit()

        socketio.emit('user_role_changed', {
            'user_id': user.id,
            'username': user.username,
            'new_role': 'user',
            'changed_by': ctx.username,
            'action': 'demote'
        }, broadcast=True)

        self._log_action(ctx.user_id, 'demote', user.id)

        return PluginResponse.ok(
            f"Пользователь `{user.username}` лишён роли администратора.\n"
            f"Права снял: `{ctx.username}`"
        )

    @staticmethod
    def _find_user(identifier: str) -> User:
        import re

        if identifier.isdigit():
            return User.query.get(int(identifier))

        user = User.query.filter_by(username=identifier).first()
        if user:
            return user

        return User.query.filter(
            User.username.ilike(f"%{re.escape(identifier)}%")
        ).first()

    @staticmethod
    def _log_action(admin_id: int, action: str, target_id: int):
        action_names = {'promote': 'PROMOTE', 'demote': 'DEMOTE'}
        log_msg = (
            f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] "
            f"Admin#{admin_id} → {action_names.get(action, action.upper())} User#{target_id}"
        )
        print(f"AdminLog: {log_msg}")

    @staticmethod
    def help() -> str:
        return (
            "Управление ролями\n"
            "\n"
            "//admin <username|id>    — Назначить администратора\n"
            "//deadmin <username|id>  — Снять роль администратора\n"
            "\n"
            "Примеры:\n"
            "  //admin moderator\n"
            "  //admin 42\n"
            "  //deadmin moderator"
        )