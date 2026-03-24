from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash

from extensions import db
from models import User, Message

profile_bp = Blueprint('profile', __name__, url_prefix='/profile')


@profile_bp.route('')
@login_required
def profile():
    message_count = Message.query.filter_by(user_id=current_user.id).count()
    last_message = Message.query.filter_by(user_id=current_user.id).order_by(Message.timestamp.desc()).first()
    return render_template('profile.html', user=current_user, is_own=True,
                           message_count=message_count, last_message=last_message)


@profile_bp.route('/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip().lower()
        current_password = request.form.get('current_password', '')
        new_password = request.form.get('new_password', '')
        confirm_password = request.form.get('confirm_password', '')

        errors = []
        if not username or len(username) < 2:
            errors.append('Имя должно быть не менее 2 символов')
        if not email or '@' not in email:
            errors.append('Некорректный email')
        if new_password:
            if len(new_password) < 6:
                errors.append('Пароль должен быть не менее 6 символов')
            if new_password != confirm_password:
                errors.append('Пароли не совпадают')
            if not check_password_hash(current_user.password, current_password):
                errors.append('Неверный текущий пароль')

        existing_user = User.query.filter_by(email=email).first()
        if existing_user and existing_user.id != current_user.id:
            errors.append('Этот email уже используется')

        if errors:
            for error in errors:
                flash(error, 'error')
            return render_template('profile_edit.html', user=current_user)

        current_user.username = username
        current_user.email = email
        if new_password:
            current_user.password = generate_password_hash(new_password, method='pbkdf2:sha256')

        db.session.commit()
        flash('Профиль обновлён ✓', 'success')
        return redirect(url_for('profile.profile'))

    return render_template('profile_edit.html', user=current_user)


@profile_bp.route('/<int:user_id>')
@login_required
def view_user_profile(user_id):
    user = db.get_or_404(User, user_id)
    message_count = Message.query.filter_by(user_id=user_id).count()
    last_message = Message.query.filter_by(user_id=user_id).order_by(Message.timestamp.desc()).first()
    return render_template('profile.html', user=user, is_own=False,
                           message_count=message_count, last_message=last_message)


@profile_bp.route('/avatar', methods=['POST'])
@login_required
def update_avatar():
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
        flash('Аватар сброшен', 'success')
    return redirect(url_for('profile.profile'))
