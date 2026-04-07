from extensions import db
from datetime import datetime, timezone


class Bot(db.Model):
    __tablename__ = 'bots'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), unique=True, nullable=False)
    username = db.Column(db.String(150), unique=True, nullable=False)
    description = db.Column(db.Text, default='')
    avatar_url = db.Column(db.String(500), default='')

    is_active = db.Column(db.Boolean, default=True)
    is_public = db.Column(db.Boolean, default=False)
    auto_reply = db.Column(db.Boolean, default=False)
    reply_keywords = db.Column(db.Text, default='')
    messages_sent = db.Column(db.Integer, default=0)
    last_active = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    schedule_enabled = db.Column(db.Boolean, default=False)
    schedule_config = db.Column(db.Text, default='')
    created_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))

    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    owner = db.relationship('User', back_populates='owned_bots')

    messages = db.relationship('Message', back_populates='bot', lazy='dynamic')

    def __repr__(self):
        return f'<Bot {self.name}>'

    def get_avatar(self) -> str:
        if self.avatar_url:
            return self.avatar_url
        return f'https://ui-avatars.com/api/?name={self.name}&background=7c3aed&color=fff&size=200'

    def can_send_message(self) -> tuple[bool, str]:
        if not self.is_active:
            return False, "Бот не активен"
        if not self.owner.is_verified:
            return False, "Владелец не подтверждён"
        return True, ""

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'name': self.name,
            'username': self.username,
            'description': self.description,
            'avatar_url': self.get_avatar(),
            'owner_id': self.owner_id,
            'is_active': self.is_active,
            'is_public': self.is_public,
            'messages_sent': self.messages_sent,
            'created_at': self.created_at.strftime('%d.%m.%Y') if self.created_at else None
        }