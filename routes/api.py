from flask import Blueprint, request, jsonify

from extensions import db, socketio
from models import User, Message

api_bp = Blueprint('api', __name__, url_prefix='/api')


@api_bp.route('/bot/send_message', methods=['POST'])
def bot_send_message():
    try:
        api_key = request.headers.get('X-API-Key')

        if not api_key:
            return jsonify({'error': 'Требуется заголовок X-API-Key'}), 401

        bot = User.query.filter_by(api_key=api_key, is_bot=True).first()
        if not bot:
            print(f"❌ Бот не найден для ключа: {api_key[:16]}...")
            return jsonify({'error': 'Неверный API ключ или пользователь не является ботом'}), 403

        if not request.is_json:
            return jsonify({'error': 'Content-Type должен быть application/json'}), 400

        data = request.get_json()
        content = data.get('message', '').strip() if data else ''

        if not content:
            return jsonify({'error': 'Сообщение не может быть пустым'}), 400

        msg = Message(content=content, user_id=bot.id)
        db.session.add(msg)
        db.session.commit()

        socketio.emit('new_message', {
            'id': msg.id,
            'text': msg.content,
            'username': bot.username,
            'time': msg.timestamp.strftime('%H:%M'),
            'user_id': bot.id,
            'user_new_id': bot.user_id,
            'user_avatar': bot.get_avatar()
        })

        print(f"🤖 Бот {bot.username} отправил: {content[:50]}")

        return jsonify({
            'success': True,
            'message_id': msg.id,
            'timestamp': msg.timestamp.isoformat()
        }), 200

    except Exception as e:
        import traceback
        print(f"❌ Ошибка в bot_send_message: {type(e).__name__}: {e}")
        traceback.print_exc()
        return jsonify({'error': f'Внутренняя ошибка сервера: {str(e)}'}), 500
