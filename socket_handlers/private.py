from flask import request
from flask_login import current_user
from flask_socketio import emit, join_room

from extensions import db
from models import User, PrivateMessage


def register_private_handlers(socketio: ...) -> None:
    @socketio.on('join_private_room')
    def on_join_private_room(data: dict[str, ...]) -> None:
        user_id = data.get('user_id')
        if user_id and user_id == current_user.id:
            room = f'user_{user_id}'
            join_room(room)
            print(f"{current_user.username} присоединился к комнате {room}")

    @socketio.on('send_private_message')
    def on_send_private_message(data: dict[str, ...]) -> None:
        if not current_user.is_authenticated:
            emit('error', {'message': 'Не авторизован'}, room=request.sid)
            return

        recipient_id = data.get('recipient_id')
        content = data.get('content', '').strip()

        if not recipient_id or not content:
            emit('error', {'message': 'Некорректные данные'}, room=request.sid)
            return

        recipient = User.query.get(recipient_id)
        if not recipient:
            emit('error', {'message': 'Пользователь не найден'}, room=request.sid)
            return

        msg = PrivateMessage(
            content=content,
            sender_id=current_user.id,
            recipient_id=recipient_id
        )
        db.session.add(msg)
        db.session.commit()

        message_data = {
            'id': msg.id,
            'content': msg.content,
            'timestamp': msg.timestamp.strftime('%H:%M'),
            'sender_id': current_user.id,
            'sender_username': current_user.username,
            'recipient_id': recipient_id,
            'sender_avatar': current_user.avatar_url
        }

        emit('private_message', message_data, room=f'user_{recipient_id}')
        emit('private_message_sent', message_data, room=f'user_{current_user.id}')
        print(f"Личное сообщение: {current_user.username} -> {recipient.username}")

    @socketio.on('private_message_edited')
    def on_private_message_edited(data: dict[str, ...]) -> None:
        pass

    @socketio.on('private_message_deleted')
    def on_private_message_deleted(data: dict[str, ...]) -> None:
        pass