from flask_mail import Message
from extensions import mail


def send_verification_email_with_token(email: str, token: str) -> bool:
    try:
        short_code = token[:6].upper()
        link = f"http://127.0.0.1:8080/verify?token={token}"

        msg = Message(
            subject="Подтвердите email — Nexus Messenger",
            recipients=[email],
            html=f"""
            <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #1e40af;">Добро пожаловать в Nexus Messenger!</h2>
                <p>Ваш код подтверждения:</p>
                <div style="background: #f3f4f6; padding: 16px; font-size: 24px; font-weight: bold; text-align: center; border-radius: 8px; margin: 20px 0;">
                    {short_code}
                </div>
                <p>Или просто нажмите кнопку ниже:</p>
                <a href="{link}" 
                   style="display: inline-block; background: #3b82f6; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; font-weight: bold;">
                    Подтвердить email
                </a>
                <p>Ссылка действительна 10 минут.</p>
                <hr>
                <p style="color: #647481; font-size: 12px;">
                    Nexus Messenger • © 2026
                </p>
            </div>
            """
        )
        mail.send(msg)
        return True
    except Exception as e:
        print(f"[EMAIL ERROR] {e}")
        return False
