from flask_mail import Message

from extensions import mail
from static.email_text import email_text


def send_verification_email_with_token(email: str, token: str) -> bool:
    try:
        short_code = token[:6].upper()
        link = f"http://vladimirevgenevichpostavtestoballovpozhaluista-ru.fun/verify?token={token}"

        msg = Message(
            subject="Подтвердите email — Nexus Messenger",
            recipients=[email],
            html=email_text(short_code, link),
        )
        mail.send(msg)
        return True
    except Exception as e:
        print(f"EMAIL ERROR: {e}")
        return False
