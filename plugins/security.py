import re


class SecurityPolicy:
    DANGEROUS_CHARS = [';', '|', '`', '$', '(', ')', '{', '}', '[', ']', '&', '!', '\\']

    MAX_ARG_LENGTH = 500

    USER_COMMANDS = {
        'help', 'echo', 'roll', 'theme', 'game'
    }

    ADMIN_COMMANDS = {
        'reload', 'plugins', 'ban', 'kick'
    }

    @classmethod
    def sanitize_arg(cls, arg: str) -> str:
        for char in cls.DANGEROUS_CHARS:
            arg = arg.replace(char, '')
        return arg.strip()[:cls.MAX_ARG_LENGTH]

    @classmethod
    def validate_command(cls, command: str, args: list[str], is_admin: bool) -> tuple[bool, str]:
        cmd_lower = command.lower()

        if cmd_lower in cls.ADMIN_COMMANDS and not is_admin:
            return False, "Доступ запрещён"

        for arg in args:
            if any(char in arg for char in cls.DANGEROUS_CHARS):
                return False, "Недопустимые символы в аргументах"
            if len(arg) > cls.MAX_ARG_LENGTH:
                return False, "Аргумент слишком длинный"

        return True, ""

    @classmethod
    def is_safe_theme_name(cls, name: str) -> bool:
        if not name or len(name) > 50:
            return False
        return bool(re.match(r'^[a-zA-Z0-9_\-\s]+$', name))
