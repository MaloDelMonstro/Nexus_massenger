from datetime import datetime, timedelta, timezone
import secrets

from extensions import db
from models import User, VerificationToken
from services.user_service import create_user
from utils.email import send_verification_email_with_token


def register_user_and_send_verification(
        email: str,
        username: str,
        password: str,
        region: int,
) -> tuple[User | None, list[str]]:
    user, errors = create_user(email, username, password, region)
    if errors:
        return None, errors

    token = secrets.token_urlsafe(32)
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=10)

    token_record = VerificationToken(
        user_id=user.id,
        token=token,
        expires_at=expires_at,
        used=False,
    )
    db.session.add(token_record)

    if not send_verification_email_with_token(email, token):
        db.session.rollback()
        return None, ["Ошибка отправки email"]

    db.session.commit()
    return user, []


def verify_token(token: str) -> tuple[bool, str, int | None]:
    token_record = VerificationToken.query.filter_by(token=token, used=False).first()
    if not token_record:
        return False, "Токен недействителен или уже использован", None

    if not token_record.is_valid():
        token_record.used = True
        db.session.commit()
        return False, "Токен истёк", None

    token_record.used = True
    db.session.commit()
    return True, "OK", token_record.user_id


def regenerate_verification_token(email: str) -> tuple[bool, str]:
    user = User.query.filter_by(email=email).first()
    if not user:
        return False, "Пользователь не найден"

    if user.is_verified:
        return False, "Email уже подтверждён"

    VerificationToken.query.filter_by(user_id=user.id).delete()

    token = secrets.token_urlsafe(32)
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=10)

    new_token_record = VerificationToken(
        user_id=user.id,
        token=token,
        expires_at=expires_at,
        used=False,
    )
    db.session.add(new_token_record)

    if not send_verification_email_with_token(email, token):
        db.session.rollback()
        return False, "Ошибка отправки email"

    db.session.commit()
    return True, "Новый код отправлен"
