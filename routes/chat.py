from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user, logout_user
from services.chat_service import (get_chat_profile_data, get_top_users, get_recent_messages, get_active_users,
                                   get_conversations)
from services.message_service import (get_recent_messages as get_gen_messages, edit_message as svc_edit_message,
                                      delete_message as svc_delete_message)
from extensions import socketio

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
        flash('Подтвердите email', 'warning')
        return redirect(url_for('auth.verify_email', email=current_user.email))

    if current_user.is_banned:
        flash('Аккаунт заблокирован', 'error')
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


@chat_bp.route('/chat/profile')
@login_required
def chat_profile():
    profile_data = get_chat_profile_data()
    top_users = get_top_users()
    recent_messages = get_recent_messages()

    return render_template('chat_profile.html',
                           total_users=profile_data['total_users'],
                           total_messages=profile_data['total_messages'],
                           top_users=top_users,
                           recent_messages=recent_messages,
                           chat_name=profile_data['chat_name'],
                           chat_description=profile_data['chat_description'],
                           chat_avatar=profile_data['chat_avatar'])


@chat_bp.route('/message/<int:message_id>/edit', methods=['POST'])
@login_required
def edit_message(message_id):
    try:
        message, error = svc_edit_message(message_id, current_user.id, request.get_json().get('content', ''))

        if error:
            return jsonify({'error': error}), 400

        socketio.emit('message_edited', {
            'message_id': message.id,
            'content': message.content,
            'time': message.timestamp.strftime('%H:%M')
        })

        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@chat_bp.route('/message/<int:message_id>/delete', methods=['POST'])
@login_required
def delete_message(message_id):
    try:
        success, error = svc_delete_message(message_id, current_user.id)

        if error:
            return jsonify({'error': error}), 403

        socketio.emit('message_deleted', {'message_id': message_id})
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
