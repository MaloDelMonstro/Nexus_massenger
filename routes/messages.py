from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, Response
from flask_login import login_required, current_user

from extensions import db, socketio
from models import User, PrivateMessage

messages_bp = Blueprint('messages', __name__, url_prefix='/messages')


@messages_bp.route('')
@login_required
def messages_list() -> Response:
    return redirect(url_for('chat.chat'))


@messages_bp.route('/<int:user_id>')
@login_required
def messages_chat(user_id: int)-> Response | str:
    recipient = User.query.get_or_404(user_id)

    if recipient.id == current_user.id:
        flash('Нельзя написать самому себе', 'error')
        return redirect(url_for('messages.messages_list'))

    messages = PrivateMessage.query.filter(
        db.or_(
            db.and_(PrivateMessage.sender_id == current_user.id, PrivateMessage.recipient_id == user_id),
            db.and_(PrivateMessage.sender_id == user_id, PrivateMessage.recipient_id == current_user.id)
        )
    ).order_by(PrivateMessage.timestamp.asc()).limit(100).all()

    for msg in messages:
        if msg.recipient_id == current_user.id and not msg.is_read:
            msg.is_read = True
    db.session.commit()

    return render_template('private_messages.html', recipient=recipient, messages=messages)


@messages_bp.route('/<int:user_id>/send', methods=['POST'])
@login_required
def send_private_message(user_id: int) -> tuple[Response, int]:
    try:
        recipient = User.query.get_or_404(user_id)

        if recipient.id == current_user.id:
            return jsonify({'error': 'Нельзя написать самому себе'}), 400

        if request.is_json:
            data = request.get_json(silent=True)
        else:
            data = request.form

        if not data:
            return jsonify({'error': 'Нет данных'}), 400

        content = data.get('content', '').strip()

        if not content:
            return jsonify({'error': 'Пустое сообщение'}), 400

        msg = PrivateMessage(content=content, sender_id=current_user.id, recipient_id=user_id)
        db.session.add(msg)
        db.session.commit()

        socketio.emit('private_message', {
            'id': msg.id,
            'content': msg.content,
            'timestamp': msg.timestamp.strftime('%H:%M'),
            'sender_id': current_user.id,
            'sender_username': current_user.username,
            'recipient_id': user_id
        }, room=f'user_{user_id}')

        print(f"Личное сообщение отправлено: {current_user.username} -> {recipient.username}")
        return jsonify({'success': True, 'message_id': msg.id}), 200

    except Exception as e:
        db.session.rollback()
        print(f"Ошибка отправки: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Ошибка сервера: {str(e)}'}), 500


@messages_bp.route('/<int:message_id>/read', methods=['POST'])
@login_required
def mark_message_read(message_id: int) -> tuple[Response, int]:
    try:
        msg = PrivateMessage.query.get_or_404(message_id)
        if msg.recipient_id == current_user.id:
            msg.is_read = True
            db.session.commit()
        return jsonify({'success': True}), 200
    except Exception as e:
        db.session.rollback()
        print(f"Ошибка прочтения: {e}")
        return jsonify({'error': str(e)}), 500


@messages_bp.route('/<int:message_id>/edit', methods=['POST'])
@login_required
def edit_private_message(message_id: int) -> tuple[Response, int]:
    try:
        msg = PrivateMessage.query.get_or_404(message_id)

        if msg.sender_id != current_user.id:
            return jsonify({'error': 'Нет прав'}), 403

        if not request.is_json:
            return jsonify({'error': 'Content-Type должен быть application/json'}), 400

        data = request.get_json(silent=True)
        if not data or 'content' not in data:
            return jsonify({'error': 'Нет данных'}), 400

        new_content = data.get('content', '').strip()

        if not new_content:
            return jsonify({'error': 'Пустое сообщение'}), 400

        msg.content = new_content
        msg.edited = True
        db.session.commit()

        socketio.emit('private_message_edited', {
            'message_id': msg.id,
            'content': msg.content,
            'recipient_id': msg.recipient_id
        }, room=f'user_{msg.recipient_id}')

        print(f"Личное сообщение {message_id} отредактировано")
        return jsonify({'success': True, 'content': msg.content}), 200

    except Exception as e:
        db.session.rollback()
        print(f"Ошибка редактирования: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Ошибка сервера: {str(e)}'}), 500


@messages_bp.route('/<int:message_id>/delete', methods=['POST'])
@login_required
def delete_private_message(message_id: int) -> tuple[Response, int]:
    try:
        msg = PrivateMessage.query.get_or_404(message_id)

        if msg.sender_id != current_user.id:
            return jsonify({'error': 'Нет прав'}), 403

        msg_id = msg.id
        recipient_id = msg.recipient_id
        db.session.delete(msg)
        db.session.commit()

        socketio.emit('private_message_deleted', {
            'message_id': msg_id,
            'recipient_id': recipient_id
        }, room=f'user_{recipient_id}')

        print(f"Личное сообщение {msg_id} удалено")
        return jsonify({'success': True, 'message_id': msg_id}), 200

    except Exception as e:
        db.session.rollback()
        print(f"Ошибка удаления: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Ошибка сервера: {str(e)}'}), 500
