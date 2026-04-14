from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash, current_app
from flask_login import login_required, current_user, logout_user
from flask_socketio import emit
from datetime import datetime, timezone

from extensions import socketio
from models import Message
from services.chat_service import get_chat_profile_data, get_conversations, get_active_users
from services.message_service import (get_recent_messages as get_gen_messages, edit_message as svc_edit,
                                      delete_message as svc_delete, create_general_message)
from plugins.base import PluginContext, PluginResponse
from utils.uploads import save_uploaded_image

chat_bp = Blueprint('chat', __name__)


@chat_bp.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('chat.chat'))
    return redirect(url_for('auth.login'))


@chat_bp.route('/chat')
@login_required
def chat():
    if not current_user.is_verified:
        flash('Подтвердите email для доступа к чату', 'warning')
        return redirect(url_for('auth.verify_email', email=current_user.email))

    if current_user.is_banned:
        flash('Ваш аккаунт заблокирован', 'error')
        logout_user()
        return redirect(url_for('auth.login'))

    messages = get_gen_messages(50)
    conversations = get_conversations(current_user.id)
    active_users = get_active_users()
    profile_data = get_chat_profile_data()

    return render_template(
        'chat.html',
        messages=messages,
        conversations=conversations,
        active_users=active_users,
        chat_name=profile_data['chat_name'],
        chat_avatar=profile_data['chat_avatar']
    )


@socketio.on('connect')
def handle_connect():
    if current_user.is_authenticated:
        emit('user_connected', {'user_id': current_user.id})


@socketio.on('disconnect')
def handle_disconnect():
    pass


@socketio.on('send_message')
def handle_send_message(data):
    if not current_user.is_authenticated:
        emit('error', {'message': 'Вы не авторизованы'})
        return

    content = data.get('message', '').strip()
    image_url = data.get('image_url')

    if not content and not image_url:
        return

    user = current_user._get_current_object()
    now = datetime.now(timezone.utc)

    if content.startswith('/'):
        plugin_mgr = current_app.extensions.get('plugin_manager')
        if plugin_mgr:
            ctx = PluginContext(
                user_id=user.id,
                username=user.username,
                user_is_admin=user.is_admin,
                chat_id=1,
                timestamp=now
            )
            try:
                print(f"Выполнение команды: {content}")
                response: PluginResponse = plugin_mgr.execute_command(content, ctx)

                if response:
                    print(f"Ответ плагина: {response.message[:100]}")

                    emit_data = {
                        'id': -999,
                        'text': response.message,
                        'username': 'Nexus Bot',
                        'time': now.strftime('%H:%M'),
                        'user_id': 0,
                        'user_new_id': 'BOT',
                        'user_avatar': None,
                        'is_bot': True
                    }

                    socketio.emit('new_message', emit_data)
                    return

            except Exception as e:
                print(f"Ошибка плагина: {e}")
                import traceback
                traceback.print_exc()

    try:
        display_content = "[Фото отправлено]" if image_url else content

        msg = create_general_message(display_content, user.id, image_url=image_url)

        emit_data = {
            'id': msg.id,
            'text': msg.content,
            'image_url': msg.image_url,
            'username': user.username,
            'time': msg.timestamp.strftime('%H:%M'),
            'user_id': user.id,
            'user_new_id': user.user_id,
            'user_avatar': user.get_avatar() if hasattr(user, 'get_avatar') else None
        }

        socketio.emit('new_message', emit_data)

    except Exception as e:
        print(f"Ошибка отправки: {e}")
        emit('error', {'message': 'Ошибка при отправке'})


@socketio.on('request_edit')
def handle_request_edit(data):
    message_id = data.get('message_id')
    if not current_user.is_authenticated: return

    msg = Message.query.get(message_id)
    if msg and msg.user_id == current_user.id:
        emit('edit_allowed', {
            'message_id': message_id,
            'content': msg.content
        })


@socketio.on('request_delete')
def handle_request_delete(data):
    message_id = data.get('message_id')
    if not current_user.is_authenticated: return

    msg = Message.query.get(message_id)
    if msg and msg.user_id == current_user.id:
        emit('delete_allowed', {'message_id': message_id})


@chat_bp.route('/message/<int:message_id>/edit', methods=['POST'])
@login_required
def api_edit_message(message_id):
    data = request.get_json()
    content = data.get('content', '').strip()

    message, error = svc_edit(message_id, current_user.id, content)
    if error:
        return jsonify({'error': error}), 403

    socketio.emit('message_edited', {
        'message_id': message.id,
        'content': message.content
    })

    return jsonify({'success': True})


@chat_bp.route('/message/<int:message_id>/delete', methods=['POST'])
@login_required
def api_delete_message(message_id):
    success, error = svc_delete(message_id, current_user.id)
    if not success:
        return jsonify({'error': error}), 403

    socketio.emit('message_deleted', {'message_id': message_id})
    return jsonify({'success': True})


@chat_bp.route('/upload-image', methods=['POST'])
@login_required
def upload_image():
    if 'image' not in request.files:
        return jsonify({'error': 'Файл не выбран'}), 400

    file = request.files['image']

    url, error = save_uploaded_image(file)

    if error:
        return jsonify({'error': error}), 400

    return jsonify({'url': url})
