from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, current_user
from services.user_service import create_user, authenticate_user
from extensions import db
from models import VerificationCode
from utils.helpers import generate_code
from datetime import datetime, timezone, timedelta
from utils.email import send_verification_email

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('chat.chat'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')

        user = authenticate_user(email, password)

        if user:
            login_user(user)
            flash('Вход выполнен', 'success')
            return redirect(url_for('chat.chat'))
        else:
            flash('Неверный email или пароль', 'error')

    return render_template('auth.html', mode='login')


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('chat.chat'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        region = request.form.get('region', '1')

        user, errors = create_user(email, username, password, int(region))

        if errors:
            for error in errors:
                flash(error, 'error')
            return redirect(url_for('auth.register'))

        code = generate_code()
        expires_at = datetime.now(timezone.utc) + timedelta(minutes=10)
        verification = VerificationCode(email=email, code=code, expires_at=expires_at)
        db.session.add(verification)
        db.session.commit()

        if send_verification_email(email, code):
            flash('Код подтверждения отправлен', 'success')
            return redirect(url_for('auth.verify_email', email=email))
        else:
            flash('Ошибка отправки email', 'error')
            return redirect(url_for('auth.register'))

    return render_template('auth.html', mode='register')


@auth_bp.route('/logout')
def logout():
    from flask_login import logout_user
    logout_user()
    return redirect(url_for('auth.login'))
