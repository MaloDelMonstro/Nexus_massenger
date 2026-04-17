def email_text(short_code: str, link: str) -> str:
    return f"""
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
