def validate_email(email: str) -> tuple[bool, str | None]:
    if not email:
        return False, 'Email не может быть пустым'
    if '@' not in email or '.' not in email:
        return False, 'Некорректный email'
    if len(email) > 150:
        return False, 'Email слишком длинный'
    return True, None


def validate_password(password: str, min_length: int = 8) -> tuple[bool, str | None]:
    if not password:
        return False, 'Пароль не может быть пустым'
    if len(password) < min_length:
        return False, f'Пароль должен быть не менее {min_length} символов'
    return True, None


def validate_username(username: str, min_length: int = 5, max_length: int = 100) -> tuple[bool, str | None]:
    if not username:
        return False, 'Имя пользователя не может быть пустым'
    if len(username) < min_length:
        return False, f'Имя должно быть не менее {min_length} символов'
    if len(username) > max_length:
        return False, f'Имя должно быть не более {max_length} символов'
    return True, None


def validate_url(url: str | None) -> tuple[bool, str | None]:
    if not url:
        return True, None
    if not (url.startswith('http://') or url.startswith('https://')):
        return False, 'URL должен начинаться с http:// или https://'
    return True, None
