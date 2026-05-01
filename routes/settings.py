from flask import Blueprint, render_template, request, redirect, url_for, flash, Response
from flask_login import login_required, current_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash

from extensions import db
from models import User, Message

settings_bp = Blueprint('settings', __name__, url_prefix='/settings')


@settings_bp.route('')
@login_required
def settings() -> str:
    return render_template('settings.html')


@settings_bp.route('/profile', methods=['POST'])
@login_required
def settings_profile() -> Response:
    username = request.form.get('username', '').strip()
    email = request.form.get('email', '').strip().lower()
    avatar_url = request.form.get('avatar_url', '').strip()

    errors = []

    if not username or len(username) < 4:
        errors.append('Имя должно быть не менее 4 символов')
    if not email or '@' not in email:
        errors.append('Некорректный email')

    existing_user = User.query.filter_by(email=email).first()
    if existing_user and existing_user.id != current_user.id:
        errors.append('Этот email уже используется')

    if avatar_url and not avatar_url.startswith(('http://', 'https://')):
        errors.append('URL аватара должен начинаться с http:// или https://')

    if errors:
        for error in errors:
            flash(error, 'error')
        return redirect(url_for('settings.settings'))

    current_user.username = username
    current_user.email = email
    current_user.avatar_url = avatar_url
    db.session.commit()

    flash('Профиль обновлён', 'success')
    return redirect(url_for('settings.settings'))


@settings_bp.route('/privacy', methods=['POST'])
@login_required
def settings_privacy() -> Response:
    try:
        current_user.privacy_show_email = request.form.get('privacy_show_email') == '1'
        current_user.privacy_show_user_id = request.form.get('privacy_show_user_id') == '1'
        current_user.privacy_show_online = request.form.get('privacy_show_online') == '1'
        current_user.privacy_show_last_seen = request.form.get('privacy_show_last_seen') == '1'

        current_user.privacy_allow_messages_from = request.form.get('privacy_allow_messages_from', 'all')

        db.session.commit()
        flash('Настройки конфиденциальности сохранены', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Ошибка сохранения: {str(e)}', 'error')

    return redirect(url_for('settings.settings'))


@settings_bp.route('/password', methods=['POST'])
@login_required
def settings_password() -> Response:
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
    flash('Пароль изменён', 'success')
    return redirect(url_for('settings.settings'))


@settings_bp.route('/avatar', methods=['POST'])
@login_required
def settings_avatar() -> Response:
    avatar_url = request.form.get('avatar_url', '').strip()

    if avatar_url:
        if avatar_url.startswith(('http://', 'https://')):
            current_user.avatar_url = avatar_url
            db.session.commit()
            flash('Аватар обновлён', 'success')
        else:
            flash('Некорректный URL аватара', 'error')
    else:
        current_user.avatar_url = None
        db.session.commit()
        flash('Аватар сброшен', 'success')

    return redirect(url_for('settings.settings'))


@settings_bp.route('/delete-account', methods=['POST'])
@login_required
def delete_account() -> Response:
    password = request.form.get('password', '')

    if not check_password_hash(current_user.password, password):
        flash('Неверный пароль', 'error')
        return redirect(url_for('settings.settings'))

    Message.query.filter_by(user_id=current_user.id).delete()
    user_email = current_user.email
    user_id = current_user.id

    logout_user()

    user_to_delete = User.query.get(user_id)
    if user_to_delete:
        db.session.delete(user_to_delete)

    db.session.commit()
    flash(f'Аккаунт {user_email} удалён', 'info')
    return redirect(url_for('auth.login'))
