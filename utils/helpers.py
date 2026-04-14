from datetime import datetime, timezone
import secrets


def generate_verification_code() -> str:
    return f"{secrets.randbelow(900_000) + 100_000}"


def ensure_aware(dt: datetime | None) -> datetime:
    if dt is None:
        return datetime.now(timezone.utc)
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt


def get_avatar_url(username: str, avatar_url: str | None = None) -> str:
    if avatar_url:
        return avatar_url
    return f'https://ui-avatars.com/api/?name={username}&background=6366f1&color=fff&size=200'


def format_datetime(date: datetime | None, format_str: str = '%d.%m.%Y %H:%M') -> str:
    if not date:
        return 'Неизвестно'
    return date.strftime(format_str)


def truncate_text(text: str | None, length: int = 100) -> str:
    if not text:
        return ''
    if len(text) <= length:
        return text
    return text[:length] + '...'
