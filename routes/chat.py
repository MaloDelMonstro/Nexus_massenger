from flask import Blueprint, render_template, redirect, url_for, flash, jsonify, request, Response
from flask_login import login_required, current_user, logout_user
from datetime import datetime, timezone, timedelta

from extensions import db, socketio
from models import Message, User, PrivateMessage

chat_bp = Blueprint('chat', __name__, url_prefix='')


@chat_bp.route('/')
def index() -> Response:
    if current_user.is_authenticated:
        return redirect(url_for('chat.chat'))
    return redirect(url_for('auth.login'))


@chat_bp.route('/chat')
@login_required
def chat() -> Response | str:
    if not current_user.is_verified:
        flash('Подтвердите email', 'warning')
        return redirect(url_for('auth.verify_email', email=current_user.email))

    if current_user.is_banned:
        flash(f'Аккаунт заблокирован: {current_user.ban_reason}', 'error')
        logout_user()
        return redirect(url_for('auth.login'))

    messages = Message.query.order_by(Message.timestamp.desc()).limit(50).all()
    messages.reverse()

    conversations = db.session.query(
        User,
        db.func.count(PrivateMessage.id).label('unread_count'),
        db.func.max(PrivateMessage.timestamp).label('last_message_time')
    ).outerjoin(
        PrivateMessage,
        db.and_(
            db.or_(
                PrivateMessage.sender_id == current_user.id,
                PrivateMessage.recipient_id == current_user.id
            ),
            PrivateMessage.is_read == False,
            PrivateMessage.recipient_id == current_user.id
        )
    ).filter(
        db.or_(
            PrivateMessage.sender_id == current_user.id,
            PrivateMessage.recipient_id == current_user.id
        )
    ).group_by(User.id).order_by(
        db.func.max(PrivateMessage.timestamp).desc().nullslast()
    ).all()

    if not conversations:
        users = User.query.filter(User.id != current_user.id).order_by(User.created_at.desc()).limit(10).all()
        conversations = [(u, 0, None) for u in users]

    unread_count = PrivateMessage.query.filter_by(
        recipient_id=current_user.id,
        is_read=False
    ).count()

    admin = User.query.filter_by(is_admin=True).first()
    if admin:
        db.session.expire(admin)

    chat_name = admin.chat_name if admin and admin.chat_name else 'Nexus Chat'
    chat_avatar = admin.chat_avatar if admin and admin.chat_avatar else None

    five_minutes_ago = datetime.now(timezone.utc) - timedelta(minutes=5)
    active_users = User.query.filter(
        User.id.in_(
            db.session.query(Message.user_id).filter(
                Message.timestamp >= five_minutes_ago
            ).distinct()
        )
    ).count()

    return render_template(
        'chat.html',
        messages=messages,
        chat_name=chat_name,
        chat_avatar=chat_avatar,
        active_users=active_users or 1,
        unread_count=unread_count,
        conversations=conversations
    )


@chat_bp.route('/chat/profile')
@login_required
def chat_profile() -> str:
    admin = User.query.filter_by(is_admin=True).first()
    if admin:
        db.session.expire(admin)
        db.session.refresh(admin)

    chat_name = admin.chat_name if admin and admin.chat_name else 'Nexus Chat'
    chat_description = admin.chat_description if admin and admin.chat_description else 'Общий чат мессенджера'
    chat_avatar = admin.chat_avatar if admin and admin.chat_avatar else None

    total_users = User.query.count()
    total_messages = Message.query.count()

    top_users = db.session.query(
        User.username,
        User.avatar_url,
        db.func.count(Message.id).label('message_count')
    ).join(Message).group_by(User.id).order_by(
        db.func.count(Message.id).desc()
    ).limit(5).all()

    recent_messages = Message.query.order_by(Message.timestamp.desc()).limit(10).all()

    return render_template(
        'chat_profile.html',
        total_users=total_users,
        total_messages=total_messages,
        top_users=top_users,
        recent_messages=recent_messages,
        chat_name=chat_name,
        chat_description=chat_description,
        chat_avatar=chat_avatar
    )


@chat_bp.route('/message/<int:message_id>/edit', methods=['POST'])
@login_required
def edit_message(message_id: int) -> tuple[Response, int]:
    try:
        message = db.get_or_404(Message, message_id)

        if message.user_id != current_user.id:
            return jsonify({'error': 'Нет прав на редактирование'}), 403

        if not request.is_json:
            return jsonify({'error': 'Content-Type должен быть application/json'}), 400

        data = request.get_json(silent=True)
        if not data or 'content' not in data:
            return jsonify({'error': 'Нет данных'}), 400

        new_content = data.get('content', '').strip()
        if not new_content:
            return jsonify({'error': 'Сообщение не может быть пустым'}), 400

        message.content = new_content
        message.timestamp = datetime.now(timezone.utc)
        db.session.commit()

        socketio.emit('message_edited', {
            'message_id': message.id,
            'content': new_content,
            'time': message.timestamp.strftime('%H:%M')
        })

        print(f"Сообщение {message_id} отредактировано")
        return jsonify({'success': True, 'message_id': message.id}), 200

    except Exception as e:
        db.session.rollback()
        print(f"Edit error: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Ошибка сервера: {str(e)}'}), 500


@chat_bp.route('/message/<int:message_id>/delete', methods=['POST'])
@login_required
def delete_message(message_id: int) -> tuple[Response, int]:
    try:
        message = db.get_or_404(Message, message_id)

        if message.user_id != current_user.id:
            return jsonify({'error': 'Нет прав на удаление'}), 403

        msg_id = message.id
        db.session.delete(message)
        db.session.commit()

        socketio.emit('message_deleted', {'message_id': msg_id})

        print(f"Сообщение {msg_id} удалено")
        return jsonify({'success': True, 'message_id': msg_id}), 200

    except Exception as e:
        db.session.rollback()
        print(f"Delete error: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Ошибка сервера: {str(e)}'}), 500
