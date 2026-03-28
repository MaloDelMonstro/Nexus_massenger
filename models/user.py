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

    messages = db.relationship('Message', backref='user', lazy='dynamic', cascade='all, delete-orphan')

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

    def generate_api_key(self):
        self.api_key = secrets.token_hex(32)
        return self.api_key

    def __repr__(self):
        return f'<User {self.username} ({self.user_id})>'

    def get_avatar(self):
        if self.avatar_url:
            return self.avatar_url
        return f'https://ui-avatars.com/api/?name={self.username}&background=6366f1&color=fff&size=200'

    def generate_user_id(self):
        last_user = User.query.filter_by(region=self.region).order_by(User.id.desc()).first()
        if last_user and last_user.user_id:
            try:
                last_number = int(last_user.user_id.split('-')[1])
                new_number = last_number + 1
            except:
                new_number = 1
        else:
            new_number = 1
        self.user_id = f"{self.region:02d}-{new_number:08d}"
        return self.user_id