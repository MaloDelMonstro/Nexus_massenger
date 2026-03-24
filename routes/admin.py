from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import current_user

from extensions import db
from models import User, Message
from utils.decorators import admin_required

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


@admin_bp.route('')
@admin_required
def admin_panel():
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


@admin_bp.route('/chat-profile', methods=['GET', 'POST'])
@admin_required
def admin_chat_profile():
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
            flash('Профиль чата обновлён ✓', 'success')
        else:
            flash('Ошибка: не найден администратор', 'error')

        return redirect(url_for('admin.admin_chat_profile') + '?saved=1')

    return render_template('admin_chat_profile.html',
                           chat_name=admin.chat_name if admin and admin.chat_name else 'Nexus Chat',
                           chat_description=admin.chat_description if admin and admin.chat_description else 'Общий чат',
                           chat_avatar=admin.chat_avatar if admin and admin.chat_avatar else None)


@admin_bp.route('/users')
@admin_required
def admin_users():
    users = User.query.order_by(User.created_at.desc()).all()
    return render_template('admin_users.html', users=users)


@admin_bp.route('/user/<int:user_id>/toggle-admin', methods=['POST'])
@admin_required
def admin_toggle_admin(user_id):
    user = User.query.get_or_404(user_id)

    if user.id == current_user.id:
        flash('Нельзя изменить свои права', 'error')
        return redirect(url_for('admin.admin_users'))

    user.is_admin = not user.is_admin
    db.session.commit()

    flash(f'Статус администратора {"назначен" if user.is_admin else "снят"} для {user.username}', 'success')
    return redirect(url_for('admin.admin_users'))


@admin_bp.route('/user/<int:user_id>/ban', methods=['POST'])
@admin_required
def admin_ban_user(user_id):
    user = User.query.get_or_404(user_id)

    if user.id == current_user.id:
        flash('Нельзя забанить себя', 'error')
        return redirect(url_for('admin.admin_users'))

    user.is_banned = True
    user.ban_reason = request.form.get('reason', 'Нарушение правил')
    db.session.commit()

    flash(f'Пользователь {user.username} забанен', 'success')
    return redirect(url_for('admin.admin_users'))


@admin_bp.route('/user/<int:user_id>/unban', methods=['POST'])
@admin_required
def admin_unban_user(user_id):
    user = User.query.get_or_404(user_id)
    user.is_banned = False
    user.ban_reason = None
    db.session.commit()

    flash(f'Пользователь {user.username} разбанен', 'success')
    return redirect(url_for('admin.admin_users'))


@admin_bp.route('/messages')
@admin_required
def admin_messages():
    messages = Message.query.order_by(Message.timestamp.desc()).limit(100).all()
    return render_template('admin_messages.html', messages=messages)


@admin_bp.route('/message/<int:message_id>/delete', methods=['POST'])
@admin_required
def admin_delete_message(message_id):
    message = Message.query.get_or_404(message_id)
    db.session.delete(message)
    db.session.commit()
    flash('Сообщение удалено', 'success')
    return redirect(url_for('admin.admin_messages'))
