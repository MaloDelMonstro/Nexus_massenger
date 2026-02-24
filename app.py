from const import *
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_socketio import SocketIO, emit
from flask_mail import Mail, Message as MailMessage
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta, timezone
import random

app = Flask(__name__)
app.config['SECRET_KEY'] = 'nexus-secret-key-2026-change-in-production'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///chat.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = MAIL_USERNAME
app.config['MAIL_PASSWORD'] = MAIL_PASSWORD
app.config['MAIL_DEFAULT_SENDER'] = MAIL_DEFAULT_SENDER

db = SQLAlchemy(app)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')
mail = Mail(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    username = db.Column(db.String(150), nullable=False)
    is_verified = db.Column(db.Boolean, default=False)


class VerificationCode(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), nullable=False)
    code = db.Column(db.String(6), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    expires_at = db.Column(db.DateTime, nullable=False)


class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    timestamp = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc),
                          onupdate=lambda: datetime.now(timezone.utc))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref='messages')


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


def generate_code():
    return ''.join([str(random.randint(0, 9)) for _ in range(6)])


def send_verification_email(email, code):
    try:
        msg = MailMessage(
            subject='Код подтверждения Nexus Messenger',
            recipients=[email],
            body=f'Ваш код подтверждения: {code}',
            html=f'<h1>Ваш код: {code}</h1><p>Действителен 10 минут</p>'
        )
        mail.send(msg)
        print(f"✅ Письмо отправлено на {email}")
        return True
    except Exception as e:
        print(f"❌ Ошибка отправки: {e}")
        return False


@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('chat'))
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            if not user.is_verified:
                flash('Подтвердите email перед входом', 'warning')
                return redirect(url_for('verify_email', email=email))
            login_user(user)
            return redirect(url_for('chat'))
        else:
            flash('Неверный email или пароль', 'error')
    return render_template('auth.html', mode='login')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email')
        username = request.form.get('username')
        password = request.form.get('password')

        if User.query.filter_by(email=email).first():
            flash('Email уже зарегистрирован', 'error')
            return redirect(url_for('register'))

        new_user = User(
            email=email,
            username=username,
            password=generate_password_hash(password, method='pbkdf2:sha256'),
            is_verified=False
        )
        db.session.add(new_user)
        db.session.commit()

        code = generate_code()
        expires_at = datetime.now(timezone.utc) + timedelta(minutes=10)
        verification = VerificationCode(email=email, code=code, expires_at=expires_at)
        db.session.add(verification)
        db.session.commit()

        if send_verification_email(email, code):
            flash('Код отправлен на почту', 'success')
            return redirect(url_for('verify_email', email=email))
        else:
            flash('Ошибка отправки email', 'error')

    return render_template('auth.html', mode='register')


@app.route('/verify-email', methods=['GET', 'POST'])
def verify_email():
    email = request.args.get('email')
    if not email:
        return redirect(url_for('register'))

    if request.method == 'POST':
        code_input = request.form.get('code')
        verification = VerificationCode.query.filter_by(email=email, code=code_input).first()

        if verification:
            now = datetime.now(timezone.utc)
            expires = verification.expires_at

            if expires.tzinfo is None:
                expires = expires.replace(tzinfo=timezone.utc)

            if now > expires:
                flash('Код истёк', 'error')
                db.session.delete(verification)
                db.session.commit()
                return redirect(url_for('register'))

            user = User.query.filter_by(email=email).first()
            user.is_verified = True
            db.session.delete(verification)
            db.session.commit()

            flash('Email подтверждён! Теперь войдите', 'success')
            return redirect(url_for('login'))
        else:
            flash('Неверный код', 'error')

    return render_template('verify.html', email=email)


@app.route('/resend-code', methods=['POST'])
def resend_code():
    email = request.form.get('email')
    user = User.query.filter_by(email=email).first()

    if not user or user.is_verified:
        flash('Ошибка', 'error')
        return redirect(url_for('login'))

    VerificationCode.query.filter_by(email=email).delete()

    code = generate_code()
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=10)
    verification = VerificationCode(email=email, code=code, expires_at=expires_at)
    db.session.add(verification)
    db.session.commit()

    if send_verification_email(email, code):
        flash('Код отправлен', 'success')
    else:
        flash('Ошибка отправки', 'error')

    return redirect(url_for('verify_email', email=email))


@app.route('/chat')
@login_required
def chat():
    if not current_user.is_verified:
        return redirect(url_for('verify_email', email=current_user.email))
    messages = Message.query.order_by(Message.timestamp.desc()).limit(50).all()
    messages.reverse()
    return render_template('chat.html', messages=messages)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/message/<int:message_id>/edit', methods=['POST'])
@login_required
def edit_message(message_id):
    try:
        message = Message.query.get_or_404(message_id)

        if message.user_id != current_user.id:
            return jsonify({'error': 'Нет прав'}), 403

        data = request.get_json(force=True, silent=True)
        if not data or 'content' not in data:
            return jsonify({'error': 'Нет данных'}), 400

        new_content = data.get('content', '').strip()
        if not new_content:
            return jsonify({'error': 'Пустое сообщение'}), 400

        message.content = new_content
        message.timestamp = datetime.now(timezone.utc)
        db.session.commit()

        socketio.emit('message_edited', {
            'message_id': message.id,
            'content': new_content,
            'time': message.timestamp.strftime('%H:%M')
        })

        return jsonify({'success': True}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@app.route('/message/<int:message_id>/delete', methods=['POST'])
@login_required
def delete_message(message_id):
    try:
        message = Message.query.get_or_404(message_id)

        if message.user_id != current_user.id:
            return jsonify({'error': 'Нет прав'}), 403

        msg_id = message.id
        db.session.delete(message)
        db.session.commit()

        socketio.emit('message_deleted', {
            'message_id': msg_id
        })

        return jsonify({'success': True}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@socketio.on('connect')
def handle_connect():
    print(f"🔌 Клиент подключился: {request.sid}")


@socketio.on('disconnect')
def handle_disconnect():
    print(f"🔌 Клиент отключился: {request.sid}")


@socketio.on('send_message')
def handle_send_message(data):
    try:
        print(f"📩 Получено сообщение от {current_user.username if current_user.is_authenticated else 'ANON'}")
        print(f"   Данные: {data}")

        if not current_user.is_authenticated:
            emit('error', {'message': 'Не авторизован'})
            return

        if not current_user.is_verified:
            emit('error', {'message': 'Email не подтверждён'})
            return

        msg_content = data.get('message', '').strip() if isinstance(data, dict) else str(data).strip()

        if not msg_content:
            emit('error', {'message': 'Пустое сообщение'})
            return

        new_msg = Message(content=msg_content, user_id=current_user.id)
        db.session.add(new_msg)
        db.session.commit()

        print(f"✅ Сообщение сохранено (ID: {new_msg.id})")

        emit('receive_message', {
            'message': msg_content,
            'username': current_user.username,
            'time': new_msg.timestamp.strftime('%H:%M'),
            'user_id': current_user.id,
            'message_id': new_msg.id
        }, broadcast=True)

    except Exception as e:
        print(f"❌ Ошибка отправки: {e}")
        emit('error', {'message': str(e)})
        db.session.rollback()


@socketio.on('request_edit')
def handle_edit_request(data):
    try:
        print(f"✏️ Запрос на редактирование: {data}")

        if isinstance(data, dict):
            message_id = data.get('message_id')
        elif isinstance(data, (list, tuple)) and len(data) > 0:
            message_id = data[0].get('message_id') if isinstance(data[0], dict) else data[0]
        else:
            emit('edit_error', {'error': 'Неверный формат'})
            return

        if not message_id:
            emit('edit_error', {'error': 'message_id не найден'})
            return

        message = Message.query.get(message_id)
        if message and message.user_id == current_user.id:
            emit('edit_allowed', {'message_id': message.id, 'content': message.content})
        else:
            emit('edit_error', {'error': 'Нет прав'})

    except Exception as e:
        print(f"❌ Ошибка edit: {e}")
        emit('edit_error', {'error': str(e)})


@socketio.on('request_delete')
def handle_delete_request(data):
    try:
        print(f"🗑️ Запрос на удаление: {data}")

        if isinstance(data, dict):
            message_id = data.get('message_id')
        elif isinstance(data, (list, tuple)) and len(data) > 0:
            message_id = data[0].get('message_id') if isinstance(data[0], dict) else data[0]
        else:
            emit('delete_error', {'error': 'Неверный формат'})
            return

        if not message_id:
            emit('delete_error', {'error': 'message_id не найден'})
            return

        message = Message.query.get(message_id)
        if message and message.user_id == current_user.id:
            emit('delete_allowed', {'message_id': message.id})
        else:
            emit('delete_error', {'error': 'Нет прав'})

    except Exception as e:
        print(f"❌ Ошибка delete: {e}")
        emit('delete_error', {'error': str(e)})


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    print("\n🚀 Nexus Messenger запущен!")
    print(f"📍 http://127.0.0.1:{PORT}")
    print(f"http://172.21.220.65:{PORT} для теста")
    print(f"🌐 http://192.168.68.106:{PORT} (для других устройств)\n")
    socketio.run(app, debug=True, host='0.0.0.0', port=PORT, allow_unsafe_werkzeug=True)