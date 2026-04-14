from extensions import db
from models import User, VerificationCode
from services.user_service import create_user
from utils.helpers import generate_verification_code
from utils.email import send_verification_email
from datetime import datetime, timezone, timedelta


def register_user_and_send_verification(email: str, username: str, password: str, region: int)\
        -> tuple[User | None, list[str]]:
    user, errors = create_user(email, username, password, region)

    if errors:
        return None, errors

    code = generate_verification_code()
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=10)

    verification = VerificationCode(
        email=email,
        code=code,
        expires_at=expires_at
    )
    db.session.add(verification)
    db.session.commit()

    email_sent = send_verification_email(email, code)

    if not email_sent:
        return None, ['Ошибка отправки email']

    return user, []


def verify_email_code(email: str, code: str) -> tuple[bool, str]:
    from datetime import datetime, timezone

    verification = VerificationCode.query.filter_by(email=email).order_by(
        VerificationCode.created_at.desc()
    ).first()

    if not verification:
        return False, 'Код не найден'

    now = datetime.now(timezone.utc)

    expires_at = verification.expires_at
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)

    if expires_at < now:
        db.session.delete(verification)
        db.session.commit()
        return False, 'Код истёк'

    if verification.code != code:
        return False, 'Неверный код'

    user = User.query.filter_by(email=email).first()
    if not user:
        return False, 'Пользователь не найден'

    user.is_verified = True
    db.session.delete(verification)
    db.session.commit()

    return True, 'Email подтверждён'


def regenerate_verification_code(email: str) -> tuple[bool, str]:
    from datetime import datetime, timezone
    from utils.email import send_verification_email

    user = User.query.filter_by(email=email).first()
    if not user:
        return False, 'Пользователь не найден'

    if user.is_verified:
        return False, 'Email уже подтверждён'

    old_verification = VerificationCode.query.filter_by(email=email).order_by(
        VerificationCode.created_at.desc()
    ).first()

    if old_verification:
        db.session.delete(old_verification)

    code = generate_verification_code()
    expires_at = datetime.now(timezone.utc)

    verification = VerificationCode(
        email=email,
        code=code,
        expires_at=expires_at
    )
    db.session.add(verification)
    db.session.commit()

    email_sent = send_verification_email(email, code)

    if not email_sent:
        return False, 'Ошибка отправки email'

    return True, 'Новый код отправлен'


def get_verification_status(email: str) -> dict:
    user = User.query.filter_by(email=email).first()

    if not user:
        return {'exists': False}

    return {
        'exists': True,
        'is_verified': user.is_verified,
        'has_pending_code': VerificationCode.query.filter_by(email=email).count() > 0
    }