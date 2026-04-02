from flask_mail import Message as MailMessage

from extensions import mail


def send_verification_email(email: str, code: str) -> bool:
    try:
        msg = MailMessage(
            subject='Код подтверждения Nexus Messenger',
            recipients=[email],
            body=f'Ваш код подтверждения: {code}\nКод действителен 10 минут.',
            html=f'''<div style="font-family: Arial, sans-serif; padding: 20px; background: #f4f4f4;">
                        <div style="background: white; padding: 30px; border-radius: 10px; max-width: 500px; margin: 0 auto;">
                            <h2 style="color: #4F46E5;">Nexus Messenger</h2>
                            <p>Ваш код подтверждения:</p>
                            <div style="background: #EEF2FF; padding: 20px; text-align: center; border-radius: 8px;">
                                <span style="font-size: 32px; font-weight: bold; letter-spacing: 8px; color: #4F46E5;">{code}</span>
                            </div>
                            <p style="color: #6B7280; font-size: 14px;">Код действителен 10 минут.</p>
                        </div>
                    </div>
                    '''
        )
        mail.send(msg)
        print(f"Письмо отправлено на {email}")
        return True
    except Exception as e:
        print(f"Ошибка отправки email: {type(e).__name__}: {e}")
        return False