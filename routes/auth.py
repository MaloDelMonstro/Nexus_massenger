from datetime import datetime, timezone, timedelta

from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash

from extensions import db
from models import User, VerificationCode
from utils.email import send_verification_email
from utils.helpers import generate_code

auth_bp = Blueprint('auth', __name__, url_prefix='')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('chat.chat'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')

        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            if user.is_bot:
                flash('Аккаунты-боты не могут входить через веб-интерфейс', 'error')
                return redirect(url_for('auth.login'))

            login_user(user)
            next_page = request.args.get('next')
            flash('Вход выполнен ✓', 'success')
            return redirect(next_page) if next_page else redirect(url_for('chat.chat'))
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

        errors = []
        if not email or '@' not in email:
            errors.append('Некорректный email')
        if not username or len(username) < 2:
            errors.append('Имя должно быть не менее 2 символов')
        if not password or len(password) < 6:
            errors.append('Пароль должен быть не менее 6 символов')
        if User.query.filter_by(email=email).first():
            errors.append('Этот email уже зарегистрирован')

        if errors:
            for error in errors:
                flash(error, 'error')
            return redirect(url_for('auth.register'))

        new_user = User(
            email=email,
            username=username,
            password=generate_password_hash(password, method='pbkdf2:sha256'),
            is_verified=False,
            region=int(region) if region.isdigit() else 1
        )
        db.session.add(new_user)
        db.session.commit()
        new_user.generate_user_id()
        db.session.commit()

        code = generate_code()
        expires_at = datetime.now(timezone.utc) + timedelta(minutes=10)
        verification = VerificationCode(email=email, code=code, expires_at=expires_at)
        db.session.add(verification)
        db.session.commit()

        if send_verification_email(email, code):
            flash('Код подтверждения отправлен на почту', 'success')
            return redirect(url_for('auth.verify_email', email=email))
        else:
            flash('Ошибка отправки email', 'error')
            return redirect(url_for('auth.register'))

    return render_template('auth.html', mode='register')


@auth_bp.route('/verify-email', methods=['GET', 'POST'])
def verify_email():
    email = request.args.get('email', '').strip().lower()
    if not email:
        flash('Email не указан', 'error')
        return redirect(url_for('auth.register'))

    user = User.query.filter_by(email=email).first()
    if not user:
        flash('Пользователь не найден', 'error')
        return redirect(url_for('auth.register'))

    if user.is_verified:
        flash('Email уже подтверждён', 'success')
        return redirect(url_for('auth.login'))

    if request.method == 'POST':
        code_input = request.form.get('code', '').strip()
        verification = VerificationCode.query.filter_by(email=email, code=code_input).first()

        if verification:
            if verification.is_expired():
                flash('Код истёк', 'error')
                db.session.delete(verification)
                db.session.commit()
                return redirect(url_for('auth.register'))

            user.is_verified = True
            db.session.delete(verification)
            db.session.commit()
            flash('Email подтверждён! Теперь войдите.', 'success')
            return redirect(url_for('auth.login'))
        else:
            flash('Неверный код', 'error')

    return render_template('verify.html', email=email)


@auth_bp.route('/resend-code', methods=['POST'])
def resend_code():
    email = request.form.get('email', '').strip().lower()
    user = User.query.filter_by(email=email).first()

    if not user or user.is_verified:
        flash('Ошибка отправки', 'error')
        return redirect(url_for('auth.login'))

    VerificationCode.query.filter_by(email=email).delete()
    code = generate_code()
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=10)
    verification = VerificationCode(email=email, code=code, expires_at=expires_at)
    db.session.add(verification)
    db.session.commit()

    if send_verification_email(email, code):
        flash('Новый код отправлен', 'success')
    else:
        flash('Ошибка отправки', 'error')

    return redirect(url_for('auth.verify_email', email=email))


@auth_bp.route('/logout')
def logout():
    logout_user()
    flash('Вы вышли из аккаунта', 'info')
    return redirect(url_for('auth.login'))
