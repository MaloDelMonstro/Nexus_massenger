import random
from datetime import datetime, timezone


def generate_code(length: int = 6) -> str:
    return ''.join([str(random.randint(0, 9)) for _ in range(length)])


def ensure_aware(dt: datetime | None) -> datetime:
    if dt is None:
        return datetime.now(timezone.utc)
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt