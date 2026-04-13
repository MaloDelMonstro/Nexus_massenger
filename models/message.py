# models/massage.py
from extensions import db
from datetime import datetime, timezone


class Message(db.Model):
    __tablename__ = 'message'

    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    timestamp = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc),
                          onupdate=lambda: datetime.now(timezone.utc))

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True, index=True)
    user = db.relationship('User', back_populates='messages', foreign_keys=[user_id])

    bot_id = db.Column(db.Integer, db.ForeignKey('bots.id'), nullable=True)
    bot = db.relationship('Bot', back_populates='messages')

    image_url = db.Column(db.String(500), nullable=True)

    def __repr__(self) -> str:
        sender_name = self.user.username if self.user else (self.bot.name if self.bot else 'System')
        return f'<Message {self.id} by {sender_name}>'

    def to_dict(self) -> dict[str, str]:
        sender_name = self.user.username if self.user else (self.bot.name if self.bot else 'Bot')
        return {
            'id': self.id,
            'content': self.content,
            'timestamp': self.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            'user_id': self.user_id,
            'bot_id': self.bot_id,
            'username': sender_name
        }
