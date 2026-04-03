from extensions import db
from models import User
from werkzeug.security import generate_password_hash, check_password_hash
from utils.validators import validate_email, validate_password, validate_username


def create_user(email: str, username: str, password: str, region: int = 1) -> tuple[User | None, list[str]]:
    errors = []

    valid, error = validate_email(email)
    if not valid:
        errors.append(error)

    valid, error = validate_username(username)
    if not valid:
        errors.append(error)

    valid, error = validate_password(password)
    if not valid:
        errors.append(error)

    if User.query.filter_by(email=email).first():
        errors.append('Этот email уже зарегистрирован')

    if errors:
        return None, errors

    new_user = User(
        email=email,
        username=username,
        password=generate_password_hash(password, method='pbkdf2:sha256'),
        is_verified=False,
        region=region
    )
    db.session.add(new_user)
    db.session.commit()
    new_user.generate_user_id()
    db.session.commit()

    return new_user, []


def authenticate_user(email: str, password: str) -> User | None:
    user = User.query.filter_by(email=email).first()
    if user and check_password_hash(user.password, password):
        if user.is_bot:
            return None
        return user
    return None


def update_user_profile(user: User, username: str, email: str) -> tuple[bool, list[str]]:
    errors = []

    valid, error = validate_email(email)
    if not valid:
        errors.append(error)

    valid, error = validate_username(username)
    if not valid:
        errors.append(error)

    existing_user = User.query.filter_by(email=email).first()
    if existing_user and existing_user.id != user.id:
        errors.append('Этот email уже используется')

    if errors:
        return False, errors

    user.username = username
    user.email = email
    db.session.commit()

    return True, []


def change_password(user: User, current_password: str, new_password: str) -> tuple[bool, str]:
    if not check_password_hash(user.password, current_password):
        return False, 'Неверный текущий пароль'

    valid, error = validate_password(new_password)
    if not valid:
        return False, error

    user.password = generate_password_hash(new_password, method='pbkdf2:sha256')
    db.session.commit()

    return True, 'Пароль изменён'


def get_user_by_id(user_id: int) -> User | None:
    return User.query.get(user_id)


def get_user_stats(user: User) -> dict:
    from models import Message

    message_count = Message.query.filter_by(user_id=user.id).count()
    last_message = Message.query.filter_by(user_id=user.id).order_by(Message.timestamp.desc()).first()

    return {
        'message_count': message_count,
        'last_message': last_message
    }
