from extensions import db
from flask_login import UserMixin
from datetime import datetime, timezone
import secrets


class User(UserMixin, db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(20), unique=True, nullable=True, index=True)
    additional_ids = db.Column(db.Text, nullable=True)
    region = db.Column(db.Integer, default=1)
    email = db.Column(db.String(150), unique=True, nullable=False, index=True)
    password = db.Column(db.String(150), nullable=False)
    username = db.Column(db.String(150), nullable=False)
    is_verified = db.Column(db.Boolean, default=False)
    is_admin = db.Column(db.Boolean, default=False)
    is_bot = db.Column(db.Boolean, default=False)
    avatar_url = db.Column(db.String(500), nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    chat_name = db.Column(db.String(100), nullable=True)
    chat_description = db.Column(db.Text, nullable=True)
    chat_avatar = db.Column(db.String(500), nullable=True)
    api_key = db.Column(db.String(64), unique=True, nullable=True)
    admin_notes = db.Column(db.Text, nullable=True)
    admin_notes_updated = db.Column(db.DateTime, nullable=True)
    is_banned = db.Column(db.Boolean, default=False)
    ban_reason = db.Column(db.String(500), nullable=True)
    ban_until = db.Column(db.DateTime, nullable=True)

    privacy_show_email = db.Column(db.Boolean, default=False)
    privacy_show_user_id = db.Column(db.Boolean, default=True)
    privacy_show_online = db.Column(db.Boolean, default=True)
    privacy_show_last_seen = db.Column(db.Boolean, default=True)
    privacy_allow_messages_from = db.Column(db.String(20), default='all')
    privacy_blocked_users = db.Column(db.Text, nullable=True)

    sound_notifications = db.Column(db.Boolean, default=True)
    push_notifications = db.Column(db.Boolean, default=True)
    hide_email = db.Column(db.Boolean, default=False)
    show_online = db.Column(db.Boolean, default=True)

    verification_tokens = db.relationship('VerificationToken', back_populates='user', lazy='dynamic')

    owned_bots = db.relationship('Bot', back_populates='owner', lazy='dynamic')

    messages = db.relationship('Message', back_populates='user', lazy='dynamic',
                               cascade='all, delete-orphan', foreign_keys='Message.user_id')

    sent_private_messages = db.relationship('PrivateMessage',
                                            foreign_keys='PrivateMessage.sender_id',
                                            back_populates='sender',
                                            lazy='dynamic',
                                            cascade='all, delete-orphan')
    received_private_messages = db.relationship('PrivateMessage',
                                                foreign_keys='PrivateMessage.recipient_id',
                                                back_populates='recipient',
                                                lazy='dynamic',
                                                cascade='all, delete-orphan')

    def generate_api_key(self) -> str:
        self.api_key = secrets.token_hex(32)
        return self.api_key

    def __repr__(self) -> str:
        return f'<User {self.username} ({self.user_id})>'

    def get_avatar(self) -> str:
        if self.avatar_url:
            return self.avatar_url
        return f'https://ui-avatars.com/api/?name={self.username}&background=6366f1&color=fff&size=200'

    def generate_user_id(self) -> str:
        if self.region is None:
            self.region = 1

        last_user = User.query.filter(
            User.region == self.region,
            User.user_id.like(f"{self.region:02d}-%")
        ).order_by(User.user_id.desc()).first()

        if last_user and last_user.user_id:
            try:
                last_number = int(last_user.user_id.split('-')[1])
                new_number = last_number + 1
            except (ValueError, IndexError):
                new_number = 1
        else:
            new_number = 1

        self.user_id = f"{self.region:02d}-{new_number:08d}"
        return self.user_id

    @property
    def all_ids(self) -> list[tuple[str, str]]:
        ids = []
        if self.user_id:
            ids.append(('Основной', self.user_id))

        if self.additional_ids:
            additional = [id.strip() for id in self.additional_ids.split(',') if id.strip()]
            for i, id_val in enumerate(additional[:2], 1):
                prefix = ['Второй', 'Третий'][i - 1]
                ids.append((prefix, id_val))

        return ids
