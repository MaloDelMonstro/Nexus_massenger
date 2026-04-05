from flask import Blueprint, render_template, request, redirect, url_for, flash, Response
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash

from extensions import db
from models import User, Message

profile_bp = Blueprint('profile', __name__, url_prefix='/profile')


@profile_bp.route('')
@login_required
def profile() -> str:
    message_count = Message.query.filter_by(user_id=current_user.id).count()
    last_message = Message.query.filter_by(user_id=current_user.id).order_by(Message.timestamp.desc()).first()
    return render_template(
        'profile.html',
        user=current_user,
        is_own=True,
        message_count=message_count,
        last_message=last_message
    )


@profile_bp.route('/<int:user_id>')
@login_required
def view_user_profile(user_id: int) -> str:
    user = db.get_or_404(User, user_id)
    message_count = Message.query.filter_by(user_id=user_id).count()
    last_message = Message.query.filter_by(user_id=user_id).order_by(Message.timestamp.desc()).first()
    return render_template(
        'profile.html',
        user=user,
        is_own=False,
        message_count=message_count,
        last_message=last_message
    )


@profile_bp.route('/avatar', methods=['POST'])
@login_required
def update_avatar() -> Response:
    avatar_url = request.form.get('avatar_url', '').strip()
    if avatar_url:
        if avatar_url.startswith('http://') or avatar_url.startswith('https://'):
            current_user.avatar_url = avatar_url
            db.session.commit()
            flash('Аватар обновлён', 'success')
        else:
            flash('Некорректный URL аватара', 'error')
    else:
        current_user.avatar_url = None
        db.session.commit()
        flash('Аватар сброшен', 'success')
    return redirect(url_for('profile.profile'))
