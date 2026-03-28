from extensions import db
from datetime import datetime, timezone


class PrivateMessage(db.Model):
    __tablename__ = 'private_message'

    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    recipient_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    edited = db.Column(db.Boolean, default=False)

    sender = db.relationship('User', foreign_keys=[sender_id], back_populates='sent_private_messages')
    recipient = db.relationship('User', foreign_keys=[recipient_id], back_populates='received_private_messages')

    def __repr__(self):
        return f'<PrivateMessage {self.id}: {self.sender_id} → {self.recipient_id}>'