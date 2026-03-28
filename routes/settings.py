from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from extensions import db
from models import User

settings_bp = Blueprint('settings', __name__, url_prefix='/settings')


@settings_bp.route('')
@login_required
def settings():
    return render_template('settings.html')


@settings_bp.route('/profile', methods=['POST'])
@login_required
def settings_profile():
    username = request.form.get('username', '').strip()
    email = request.form.get('email', '').strip().lower()
    errors = []

    if not username or len(username) < 2:
        errors.append('Имя должно быть не менее 2 символов')
    if not email or '@' not in email:
        errors.append('Некорректный email')

    existing_user = User.query.filter_by(email=email).first()
    if existing_user and existing_user.id != current_user.id:
        errors.append('Этот email уже используется')

    if errors:
        for error in errors:
            flash(error, 'error')
        return redirect(url_for('settings.settings'))

    current_user.username = username
    current_user.email = email
    db.session.commit()
    flash('Профиль обновлён ✓', 'success')
    return redirect(url_for('settings.settings'))


@settings_bp.route('/password', methods=['POST'])
@login_required
def settings_password():
    current_password = request.form.get('current_password', '')
    new_password = request.form.get('new_password', '')
    confirm_password = request.form.get('confirm_password', '')
    errors = []

    if not check_password_hash(current_user.password, current_password):
        errors.append('Неверный текущий пароль')
    if new_password:
        if len(new_password) < 6:
            errors.append('Пароль должен быть не менее 6 символов')
        if new_password != confirm_password:
            errors.append('Пароли не совпадают')

    if errors:
        for error in errors:
            flash(error, 'error')
        return redirect(url_for('settings.settings'))

    current_user.password = generate_password_hash(new_password, method='pbkdf2:sha256')
    db.session.commit()
    flash('Пароль изменён ✓', 'success')
    return redirect(url_for('settings.settings'))


@settings_bp.route('/avatar', methods=['POST'])
@login_required
def settings_avatar():
    avatar_url = request.form.get('avatar_url', '').strip()
    if avatar_url:
        if avatar_url.startswith('http://') or avatar_url.startswith('https://'):
            current_user.avatar_url = avatar_url
            db.session.commit()
            flash('Аватар обновлён ✓', 'success')
        else:
            flash('Некорректный URL аватара', 'error')
    else:
        current_user.avatar_url = None
        db.session.commit()
        flash('Аватар сброшен на стандартный', 'success')
    return redirect(url_for('settings.settings'))


@settings_bp.route('/delete-account', methods=['POST'])
@login_required
def delete_account():
    from models import Message
    password = request.form.get('password', '')
    if not check_password_hash(current_user.password, password):
        flash('Неверный пароль', 'error')
        return redirect(url_for('settings.settings'))

    Message.query.filter_by(user_id=current_user.id).delete()
    user_email = current_user.email
    from flask_login import logout_user
    logout_user()
    db.session.delete(User.query.get(current_user.id))
    db.session.commit()
    flash(f'Аккаунт {user_email} удалён', 'info')
    return redirect(url_for('auth.login'))