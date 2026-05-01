from sqlalchemy.exc import SQLAlchemyError
from werkzeug.security import check_password_hash, generate_password_hash

from extensions import db
from models import Message, User
from utils.validators import validate_email, validate_password, validate_username


def create_user(email: str, username: str, password: str, region: int = 1) -> tuple[User | None, list[str]]:
    errors: list[str] = []

    valid, error = validate_email(email)
    if not valid:
        errors.append(error)

    valid, error = validate_username(username)
    if not valid:
        errors.append(error)

    valid, error = validate_password(password)
    if not valid:
        errors.append(error)

    if db.session.query(User).filter_by(email=email).first():
        errors.append("Этот email уже зарегистрирован")

    if errors:
        return None, errors

    new_user = User(
        email=email,
        username=username,
        password=generate_password_hash(password),
        is_verified=False,
        region=region,
    )
    db.session.add(new_user)

    try:
        db.session.commit()
        new_user.generate_user_id()
        db.session.commit()
        return new_user, []
    except SQLAlchemyError:
        db.session.rollback()
        raise


def authenticate_user(email: str, password: str) -> User | None:
    user = db.session.query(User).filter_by(email=email).first()
    if user and check_password_hash(user.password, password) and not getattr(user, "is_bot", False):
        return user
    return None


def update_user_profile(user: User, username: str, email: str) -> tuple[bool, list[str]]:
    errors: list[str] = []

    valid, error = validate_email(email)
    if not valid:
        errors.append(error)

    valid, error = validate_username(username)
    if not valid:
        errors.append(error)

    existing_user = db.session.query(User).filter_by(email=email).first()
    if existing_user and existing_user.id != user.id:
        errors.append("Этот email уже используется")

    if errors:
        return False, errors

    try:
        user.username = username
        user.email = email
        db.session.commit()
        return True, []
    except SQLAlchemyError:
        db.session.rollback()
        raise


def change_password(user: User, current_password: str, new_password: str) -> tuple[bool, str]:
    if not check_password_hash(user.password, current_password):
        return False, "Неверный текущий пароль"

    valid, error = validate_password(new_password)
    if not valid:
        return False, error

    try:
        user.password = generate_password_hash(new_password)
        db.session.commit()
        return True, "Пароль изменён"
    except SQLAlchemyError:
        db.session.rollback()
        raise


def get_user_by_id(user_id: int) -> User | None:
    return db.session.get(User, user_id)


def get_user_stats(user: User) -> dict[str, int | Message | None]:
    message_count: int = db.session.query(Message).filter_by(user_id=user.id).count()
    last_message: Message | None = (
        db.session.query(Message)
        .filter_by(user_id=user.id)
        .order_by(Message.timestamp.desc())
        .first()
    )
    return {"message_count": message_count, "last_message": last_message}
