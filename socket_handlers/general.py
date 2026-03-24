from flask import request
from flask_login import current_user
from flask_socketio import emit

from extensions import db
from models import Message


def register_general_handlers(socketio):
    @socketio.on('connect')
    def on_connect():
        print(
            f"🔌 WS подключён: {request.sid}, user: {current_user.username if current_user.is_authenticated else 'ANON'}")
        if not current_user.is_authenticated:
            emit('auth_error', {'message': 'Войдите в систему'}, room=request.sid)
            return False
        return True

    @socketio.on('disconnect')
    def on_disconnect():
        print(f"🔌 WS отключён: {request.sid}")

    @socketio.on('send_message')
    def on_send_message(data):
        try:
            if not current_user.is_authenticated:
                emit('error', {'message': 'Не авторизован'}, room=request.sid)
                return

            text = data.get('message', '').strip() if isinstance(data, dict) else str(data).strip()
            if not text:
                emit('error', {'message': 'Пустое сообщение'}, room=request.sid)
                return

            msg = Message(content=text, user_id=current_user.id)
            db.session.add(msg)
            db.session.commit()

            socketio.emit('new_message', {
                'id': msg.id,
                'text': msg.content,
                'username': current_user.username,
                'time': msg.timestamp.strftime('%H:%M'),
                'user_id': current_user.id,
                'user_new_id': current_user.user_id,
                'user_avatar': current_user.get_avatar()
            })

            print(f"📩 Сообщение отправлено: {current_user.username}")

        except Exception as e:
            print(f"❌ Ошибка отправки: {type(e).__name__}: {e}")
            db.session.rollback()
            emit('error', {'message': str(e)}, room=request.sid)

    @socketio.on('request_edit')
    def on_request_edit(data):
        try:
            message_id = data.get('message_id') if isinstance(data, dict) else data
            message = db.session.get(Message, message_id)

            if message and message.user_id == current_user.id:
                emit('edit_allowed', {'message_id': message.id, 'content': message.content}, room=request.sid)
            else:
                emit('edit_error', {'error': 'Нет прав'}, room=request.sid)
        except Exception as e:
            emit('edit_error', {'error': str(e)}, room=request.sid)

    @socketio.on('request_delete')
    def on_request_delete(data):
        try:
            message_id = data.get('message_id') if isinstance(data, dict) else data
            message = db.session.get(Message, message_id)

            if message and message.user_id == current_user.id:
                emit('delete_allowed', {'message_id': message.id}, room=request.sid)
            else:
                emit('delete_error', {'error': 'Нет прав'}, room=request.sid)
        except Exception as e:
            emit('delete_error', {'error': str(e)}, room=request.sid)
