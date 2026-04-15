from extensions import db
from datetime import datetime, timezone


class VerificationToken(db.Model):
    __tablename__ = 'verification_token'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    token = db.Column(db.String(128), unique=True, nullable=False, index=True)
    expires_at = db.Column(db.DateTime(timezone=True), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    used = db.Column(db.Boolean, default=False)

    user = db.relationship('User', back_populates='verification_tokens')

    def is_valid(self) -> bool:
        now = datetime.now(timezone.utc)

        expires_at = self.expires_at
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)

        return not self.used and now < expires_at
