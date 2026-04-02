from flask import Blueprint, render_template, request, redirect, url_for, flash, Response
from flask_login import current_user
from datetime import datetime, timezone

from extensions import db
from models import User, Message, PrivateMessage
from utils.decorators import admin_required

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


@admin_bp.route('')
@admin_required
def admin_panel() -> str:
    total_users = User.query.count()
    total_messages = Message.query.count()
    verified_users = User.query.filter_by(is_verified=True).count()
    banned_users = User.query.filter_by(is_banned=True).count()
    recent_users = User.query.order_by(User.created_at.desc()).limit(10).all()

    return render_template('admin_panel.html',
                           total_users=total_users,
                           total_messages=total_messages,
                           verified_users=verified_users,
                           banned_users=banned_users,
                           recent_users=recent_users)


@admin_bp.route('/user/<int:user_id>')
@admin_required
def admin_user(user_id: int) -> str:
    user = User.query.get_or_404(user_id)
    user_messages = Message.query.filter_by(user_id=user_id).order_by(Message.timestamp.desc()).limit(20).all()
    sent_private = PrivateMessage.query.filter_by(sender_id=user_id).order_by(PrivateMessage.timestamp.desc()).limit(
        10).all()
    received_private = PrivateMessage.query.filter_by(recipient_id=user_id).order_by(
        PrivateMessage.timestamp.desc()).limit(10).all()

    return render_template('admin_user.html',
                           user=user,
                           user_messages=user_messages,
                           sent_private=sent_private,
                           received_private=received_private)


@admin_bp.route('/user/<int:user_id>/toggle-admin', methods=['POST'])
@admin_required
def admin_toggle_admin(user_id: int) -> Response:
    user = User.query.get_or_404(user_id)

    if user.id == current_user.id:
        flash('Нельзя изменить свои права', 'error')
        return redirect(url_for('admin.admin_user', user_id=user_id))

    user.is_admin = not user.is_admin
    db.session.commit()

    status = 'назначен' if user.is_admin else 'снят'
    flash(f'Статус администратора {status} для {user.username}', 'success')
    return redirect(url_for('admin.admin_user', user_id=user_id))


@admin_bp.route('/user/<int:user_id>/ban', methods=['POST'])
@admin_required
def admin_ban_user(user_id: int) -> Response:
    user = User.query.get_or_404(user_id)

    if user.id == current_user.id:
        flash('Нельзя забанить себя', 'error')
        return redirect(url_for('admin.admin_user', user_id=user_id))

    reason = request.form.get('ban_reason', 'Нарушение правил')
    user.is_banned = True
    user.ban_reason = reason
    user.ban_until = datetime.now(timezone.utc)
    db.session.commit()

    flash(f'Пользователь {user.username} забанен. Причина: {reason}', 'success')
    return redirect(url_for('admin.admin_user', user_id=user_id))


@admin_bp.route('/user/<int:user_id>/unban', methods=['POST'])
@admin_required
def admin_unban_user(user_id: int) -> Response:
    user = User.query.get_or_404(user_id)
    user.is_banned = False
    user.ban_reason = None
    user.ban_until = None
    db.session.commit()

    flash(f'Пользователь {user.username} разбанен', 'success')
    return redirect(url_for('admin.admin_user', user_id=user_id))


@admin_bp.route('/user/<int:user_id>/delete', methods=['POST'])
@admin_required
def admin_delete_user(user_id: int) -> Response:
    user = User.query.get_or_404(user_id)

    if user.id == current_user.id:
        flash('Нельзя удалить себя', 'error')
        return redirect(url_for('admin.admin_user', user_id=user_id))

    username = user.username
    Message.query.filter_by(user_id=user_id).delete()
    PrivateMessage.query.filter(
        (PrivateMessage.sender_id == user_id) |
        (PrivateMessage.recipient_id == user_id)
    ).delete()

    db.session.delete(user)
    db.session.commit()

    flash(f'Пользователь {username} удалён', 'success')
    return redirect(url_for('admin.admin_panel'))


@admin_bp.route('/user/<int:user_id>/edit', methods=['POST'])
@admin_required
def admin_edit_user(user_id: int) -> Response:
    user = User.query.get_or_404(user_id)

    try:
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip().lower()
        region = request.form.get('region', type=int)
        admin_notes = request.form.get('admin_notes', '').strip()

        if not username:
            flash('Имя пользователя не может быть пустым', 'error')
            return redirect(url_for('admin.admin_user', user_id=user_id))

        user.username = username
        user.email = email
        user.region = region
        user.admin_notes = admin_notes
        user.admin_notes_updated = datetime.now(timezone.utc)

        db.session.commit()
        flash('Данные пользователя обновлены', 'success')

    except Exception as e:
        db.session.rollback()
        flash(f'Ошибка обновления: {str(e)}', 'error')

    return redirect(url_for('admin.admin_user', user_id=user_id))


@admin_bp.route('/chat-profile', methods=['GET', 'POST'])
@admin_required
def admin_chat_profile() -> Response | str:
    admin = User.query.filter_by(is_admin=True).first()

    if request.method == 'POST':
        chat_name = request.form.get('chat_name', 'Nexus Chat').strip()
        chat_description = request.form.get('chat_description', '').strip()
        chat_avatar = request.form.get('chat_avatar', '').strip()

        if admin:
            admin.chat_name = chat_name
            admin.chat_description = chat_description
            admin.chat_avatar = chat_avatar if chat_avatar else None
            db.session.commit()
            db.session.expire_all()
            flash('Профиль чата обновлён', 'success')
        else:
            flash('Ошибка: не найден администратор', 'error')

        return redirect(url_for('admin.admin_chat_profile') + '?saved=1')

    return render_template('admin_chat_profile.html',
                           chat_name=admin.chat_name if admin and admin.chat_name else 'Nexus Chat',
                           chat_description=admin.chat_description if admin and admin.chat_description else 'Общий чат',
                           chat_avatar=admin.chat_avatar if admin and admin.chat_avatar else None)


@admin_bp.route('/messages')
@admin_required
def admin_messages() -> str:
    messages = Message.query.order_by(Message.timestamp.desc()).limit(100).all()
    return render_template('admin_messages.html', messages=messages)


@admin_bp.route('/message/<int:message_id>/delete', methods=['POST'])
@admin_required
def admin_delete_message(message_id: int) -> Response:
    message = Message.query.get_or_404(message_id)
    db.session.delete(message)
    db.session.commit()
    flash('Сообщение удалено', 'success')
    return redirect(url_for('admin.admin_messages'))


@admin_bp.route('/users')
@admin_required
def admin_users() -> str:
    users = User.query.order_by(User.created_at.desc()).all()
    return render_template('admin_users.html', users=users)
