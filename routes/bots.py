from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from services.bot_service import BotService
from extensions import socketio
from models.bot import Bot
from models.message import Message

bots_bp = Blueprint('bots', __name__, url_prefix='/bots')

@bots_bp.route('/')
@login_required
def bots_list():
    user_bots = BotService.get_user_bots(current_user.id)
    public_bots = BotService.get_public_bots(10)

    return render_template('bots/list.html',
                           user_bots=user_bots,
                           public_bots=public_bots)


@bots_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_bot():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        username = request.form.get('username', '').strip()
        description = request.form.get('description', '').strip()
        avatar_url = request.form.get('avatar_url', '').strip()
        is_public = 'is_public' in request.form

        bot, errors = BotService.create_bot(
            owner_id=current_user.id,
            name=name,
            username=username,
            description=description,
            avatar_url=avatar_url,
            is_public=is_public
        )

        if errors:
            for error in errors:
                flash(error, 'error')
            return redirect(url_for('bots.create_bot'))

        flash(f'Бот "{bot.name}" создан!', 'success')
        return redirect(url_for('bots.edit_bot', bot_id=bot.id))

    return render_template('bots/create.html')


@bots_bp.route('/<int:bot_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_bot(bot_id):
    bot = BotService.get_bot_by_id(bot_id, current_user.id)
    if not bot:
        flash('Бот не найден или нет прав', 'error')
        return redirect(url_for('bots.bots_list'))

    if request.method == 'POST':
        kwargs = {
            'name': request.form.get('name', '').strip(),
            'username': request.form.get('username', '').strip(),
            'description': request.form.get('description', '').strip(),
            'avatar_url': request.form.get('avatar_url', '').strip(),
            'is_active': 'is_active' in request.form,
            'is_public': 'is_public' in request.form,
            'auto_reply': 'auto_reply' in request.form,
        }

        reply_keywords = request.form.get('reply_keywords', '{}')
        kwargs['reply_keywords'] = reply_keywords

        schedule_config = request.form.get('schedule_config', '{}')
        kwargs['schedule_config'] = schedule_config

        bot, errors = BotService.update_bot(bot_id, current_user.id, **kwargs)

        if errors:
            for error in errors:
                flash(error, 'error')
            return redirect(url_for('bots.edit_bot', bot_id=bot_id))

        flash('Настройки бота сохранены!', 'success')
        return redirect(url_for('bots.edit_bot', bot_id=bot_id))

    return render_template('bots/edit.html', bot=bot)


@bots_bp.route('/<int:bot_id>/delete', methods=['POST'])
@login_required
def delete_bot(bot_id):
    success, error = BotService.delete_bot(bot_id, current_user.id)

    if not success:
        flash(error, 'error')
    else:
        flash('Бот удалён', 'success')

    return redirect(url_for('bots.bots_list'))


@bots_bp.route('/<int:bot_id>/console')
@login_required
def bot_console(bot_id):
    bot = BotService.get_bot_by_id(bot_id, current_user.id)
    if not bot:
        flash('Бот не найден или нет прав', 'error')
        return redirect(url_for('bots.bots_list'))

    recent_messages = Message.query.filter_by(bot_id=bot_id) \
        .order_by(Message.timestamp.desc()) \
        .limit(20).all()

    return render_template('bots/console.html', bot=bot, messages=recent_messages)


@bots_bp.route('/<int:bot_id>/send', methods=['POST'])
@login_required
def send_bot_message(bot_id):
    bot = BotService.get_bot_by_id(bot_id, current_user.id)
    if not bot:
        return jsonify({'error': 'Бот не найден'}), 404

    content = request.json.get('message', '').strip() if request.is_json \
        else request.form.get('message', '').strip()

    if not content:
        return jsonify({'error': 'Сообщение не может быть пустым'}), 400

    message, error = BotService.send_message_from_bot(bot_id, content)

    if error:
        return jsonify({'error': error}), 400

    emit_data = {
        'id': message.id,
        'text': message.content,
        'username': bot.name,
        'time': message.timestamp.strftime('%H:%M'),
        'user_id': 0,
        'bot_id': bot.id,
        'bot_name': bot.name,
        'bot_avatar': bot.get_avatar(),
        'is_bot': True
    }

    socketio.emit('new_message', emit_data, broadcast=True)

    return jsonify({'success': True, 'message_id': message.id})


@bots_bp.route('/webhook/auto-reply', methods=['POST'])
def auto_reply_webhook():
    data = request.json or {}
    bot_id = data.get('bot_id')
    incoming_message = data.get('message', '')

    bot = Bot.query.get(bot_id)
    if not bot or not bot.auto_reply:
        return jsonify({'replied': False}), 200

    response = BotService.process_auto_reply(bot, incoming_message)
    if response:
        BotService.send_message_from_bot(bot_id, response)
        return jsonify({'replied': True, 'response': response}), 200

    return jsonify({'replied': False}), 200