from const import *
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_socketio import SocketIO, emit
from flask_mail import Mail, Message as MailMessage
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta, timezone
import random

app = Flask(__name__)
app.config['SECRET_KEY'] = SECRET_KEY
app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.config['MAIL_SERVER'] = MAIL_SERVER
app.config['MAIL_PORT'] = MAIL_PORT
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
login_manager.login_message = 'Пожалуйста, войдите для доступа к этой странице'
login_manager.login_message_category = 'warning'


class User(UserMixin, db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False, index=True)
    password = db.Column(db.String(150), nullable=False)
    username = db.Column(db.String(150), nullable=False)
    is_verified = db.Column(db.Boolean, default=False)
    avatar_url = db.Column(db.String(500), nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    messages = db.relationship('Message', backref='user', lazy='dynamic', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<User {self.username}>'

    def get_avatar(self):
        if self.avatar_url:
            return self.avatar_url
        return f'https://ui-avatars.com/api/?name={self.username}&background=6366f1&color=fff&size=200'


class VerificationCode(db.Model):
    __tablename__ = 'verification_code'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), nullable=False, index=True)
    code = db.Column(db.String(6), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    expires_at = db.Column(db.DateTime, nullable=False)

    def is_expired(self):
        now = datetime.now(timezone.utc)
        if self.expires_at.tzinfo is None:
            expires = self.expires_at.replace(tzinfo=timezone.utc)
        else:
            expires = self.expires_at
        return now > expires


class Message(db.Model):
    __tablename__ = 'message'

    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    timestamp = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc),
                          onupdate=lambda: datetime.now(timezone.utc))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)

    def __repr__(self):
        return f'<Message {self.id} by User {self.user_id}>'

    def to_dict(self):
        return {
            'id': self.id,
            'content': self.content,
            'timestamp': self.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            'user_id': self.user_id,
            'username': self.user.username if self.user else 'Unknown'
        }


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


def generate_code():
    return ''.join([str(random.randint(0, 9)) for _ in range(6)])


def send_verification_email(email, code):
    try:
        msg = MailMessage(
            subject='🔐 Код подтверждения Nexus Messenger',
            recipients=[email],
            body=f'Ваш код подтверждения: {code}\n\nКод действителен 10 минут.\n\nЕсли вы не регистрировались — проигнорируйте это письмо.',
            html=f'''
            <div style="font-family: Arial, sans-serif; padding: 20px; background: #f4f4f4;">
                <div style="background: white; padding: 30px; border-radius: 10px; max-width: 500px; margin: 0 auto;">
                    <h2 style="color: #4F46E5; margin: 0 0 20px 0;">Nexus Messenger</h2>
                    <p style="color: #374151; font-size: 16px;">Ваш код подтверждения:</p>
                    <div style="background: #EEF2FF; padding: 20px; text-align: center; border-radius: 8px; margin: 20px 0;">
                        <span style="font-size: 32px; font-weight: bold; letter-spacing: 8px; color: #4F46E5;">{code}</span>
                    </div>
                    <p style="color: #6B7280; font-size: 14px;">Код действителен 10 минут.</p>
                    <p style="color: #9CA3AF; font-size: 12px; margin-top: 20px;">
                        Если вы не регистрировались — проигнорируйте это письмо.
                    </p>
                </div>
            </div>
            '''
        )
        mail.send(msg)
        print(f"✅ Письмо отправлено на {email}")
        return True
    except Exception as e:
        print(f"❌ Ошибка отправки email: {type(e).__name__}: {e}")
        return False


def ensure_aware(dt):
    if dt is None:
        return datetime.now(timezone.utc)
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt


@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('chat'))
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('chat'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')

        if not email or not password:
            flash('Введите email и пароль', 'error')
            return redirect(url_for('login'))

        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            if not user.is_verified:
                flash('Подтвердите email перед входом', 'warning')
                return redirect(url_for('verify_email', email=email))

            login_user(user, remember=True)
            next_page = request.args.get('next')
            flash(f'Добро пожаловать, {user.username}!', 'success')
            return redirect(next_page if next_page else url_for('chat'))
        else:
            flash('Неверный email или пароль', 'error')

    return render_template('auth.html', mode='login')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('chat'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        errors = []
        if not email or '@' not in email:
            errors.append('Некорректный email')
        if not username or len(username) < 2:
            errors.append('Имя должно быть не менее 2 символов')
        if not password or len(password) < 6:
            errors.append('Пароль должен быть не менее 6 символов')

        if User.query.filter_by(email=email).first():
            errors.append('Этот email уже зарегистрирован')

        if errors:
            for error in errors:
                flash(error, 'error')
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
            flash('Код подтверждения отправлен на почту', 'success')
            return redirect(url_for('verify_email', email=email))
        else:
            flash('Ошибка отправки email. Попробуйте позже.', 'error')
            new_user.is_verified = True
            db.session.commit()
            flash('Регистрация успешна! Войдите.', 'success')
            return redirect(url_for('login'))

    return render_template('auth.html', mode='register')


@app.route('/verify-email', methods=['GET', 'POST'])
def verify_email():
    email = request.args.get('email', '').strip().lower()

    if not email:
        flash('Email не указан', 'error')
        return redirect(url_for('register'))

    user = User.query.filter_by(email=email).first()
    if not user:
        flash('Пользователь не найден', 'error')
        return redirect(url_for('register'))

    if user.is_verified:
        flash('Email уже подтверждён', 'success')
        return redirect(url_for('login'))

    if request.method == 'POST':
        code_input = request.form.get('code', '').strip()
        verification = VerificationCode.query.filter_by(email=email, code=code_input).first()

        if verification:
            if verification.is_expired():
                flash('Код истёк. Запросите новый.', 'error')
                db.session.delete(verification)
                db.session.commit()
                return redirect(url_for('register'))

            user.is_verified = True
            db.session.delete(verification)
            db.session.commit()

            flash('Email подтверждён! Теперь войдите.', 'success')
            return redirect(url_for('login'))
        else:
            flash('Неверный код', 'error')

    return render_template('verify.html', email=email)


@app.route('/resend-code', methods=['POST'])
def resend_code():
    email = request.form.get('email', '').strip().lower()
    user = User.query.filter_by(email=email).first()

    if not user or user.is_verified:
        flash('Ошибка отправки', 'error')
        return redirect(url_for('login'))

    VerificationCode.query.filter_by(email=email).delete()

    code = generate_code()
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=10)
    verification = VerificationCode(email=email, code=code, expires_at=expires_at)
    db.session.add(verification)
    db.session.commit()

    if send_verification_email(email, code):
        flash('Новый код отправлен', 'success')
    else:
        flash('Ошибка отправки', 'error')

    return redirect(url_for('verify_email', email=email))


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Вы вышли из аккаунта', 'info')
    return redirect(url_for('login'))


@app.route('/chat')
@login_required
def chat():
    if not current_user.is_verified:
        flash('Подтвердите email для доступа к чату', 'warning')
        return redirect(url_for('verify_email', email=current_user.email))

    messages = Message.query.order_by(Message.timestamp.desc()).limit(50).all()
    messages.reverse()
    return render_template('chat.html', messages=messages)


@app.route('/profile')
@login_required
def profile():
    message_count = Message.query.filter_by(user_id=current_user.id).count()
    last_message = Message.query.filter_by(user_id=current_user.id).order_by(Message.timestamp.desc()).first()
    return render_template('profile.html', user=current_user, is_own=True,
                           message_count=message_count, last_message=last_message)


@app.route('/profile/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip().lower()
        current_password = request.form.get('current_password', '')
        new_password = request.form.get('new_password', '')
        confirm_password = request.form.get('confirm_password', '')

        errors = []

        if not username or len(username) < 2:
            errors.append('Имя должно быть не менее 2 символов')

        if not email or '@' not in email:
            errors.append('Некорректный email')

        if new_password:
            if len(new_password) < 6:
                errors.append('Пароль должен быть не менее 6 символов')
            if new_password != confirm_password:
                errors.append('Пароли не совпадают')
            if not check_password_hash(current_user.password, current_password):
                errors.append('Неверный текущий пароль')

        existing_user = User.query.filter_by(email=email).first()
        if existing_user and existing_user.id != current_user.id:
            errors.append('Этот email уже используется')

        if errors:
            for error in errors:
                flash(error, 'error')
            return render_template('profile_edit.html', user=current_user)

        current_user.username = username
        current_user.email = email

        if new_password:
            current_user.password = generate_password_hash(new_password, method='pbkdf2:sha256')

        db.session.commit()
        flash('Профиль обновлён ✓', 'success')
        return redirect(url_for('profile'))

    return render_template('profile_edit.html', user=current_user)


@app.route('/profile/<int:user_id>')
@login_required
def view_user_profile(user_id):
    user = db.get_or_404(User, user_id)
    message_count = Message.query.filter_by(user_id=user_id).count()
    last_message = Message.query.filter_by(user_id=user_id).order_by(Message.timestamp.desc()).first()
    return render_template('profile.html', user=user, is_own=False,
                           message_count=message_count, last_message=last_message)


@app.route('/profile/avatar', methods=['POST'])
@login_required
def update_avatar():
    avatar_url = request.form.get('avatar_url', '').strip()

    if avatar_url:
        if avatar_url.startswith('http://') or avatar_url.startswith('https://'):
            current_user.avatar_url = avatar_url
            db.session.commit()
            flash('Аватар обновлён ✓', 'success')
        else:
            flash('Некорректный URL аватара', 'error')
    else:
        current_user.avatar_url = None
        db.session.commit()
        flash('Аватар сброшен', 'success')

    return redirect(url_for('profile'))


@app.before_request
def exempt_csrf_for_api():
    if request.endpoint in ['edit_message', 'delete_message']:
        setattr(request, 'csrf_exempt', True)


@app.route('/message/<int:message_id>/edit', methods=['POST'])
@login_required
def edit_message(message_id):
    try:
        message = db.get_or_404(Message, message_id)

        if message.user_id != current_user.id:
            return jsonify({'error': 'Нет прав на редактирование'}), 403

        data = request.get_json(force=True, silent=True)
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

        print(f"✅ Сообщение {message_id} отредактировано")
        return jsonify({'success': True}), 200

    except Exception as e:
        db.session.rollback()
        print(f"❌ Edit error: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/message/<int:message_id>/delete', methods=['POST'])
@login_required
def delete_message(message_id):
    try:
        message = db.get_or_404(Message, message_id)

        if message.user_id != current_user.id:
            return jsonify({'error': 'Нет прав на удаление'}), 403

        msg_id = message.id
        db.session.delete(message)
        db.session.commit()

        socketio.emit('message_deleted', {'message_id': msg_id})

        print(f"✅ Сообщение {msg_id} удалено")
        return jsonify({'success': True}), 200

    except Exception as e:
        db.session.rollback()
        print(f"❌ Delete error: {e}")
        return jsonify({'error': str(e)}), 500


@socketio.on('connect')
def on_connect():
    print(f"🔌 WS подключён: {request.sid}, user: {current_user.username if current_user.is_authenticated else 'ANON'}")
    if not current_user.is_authenticated:
        emit('auth_error', {'message': 'Войдите в систему'})
        return False
    return True


@socketio.on('disconnect')
def on_disconnect():
    print(f"🔌 WS отключён: {request.sid}")


@socketio.on('send_message')
def on_send_message(data):
    try:
        print(f"📩 Получено: {data}")

        if not current_user.is_authenticated:
            emit('error', {'message': 'Не авторизован'})
            return

        if not current_user.is_verified:
            emit('error', {'message': 'Подтвердите email'})
            return

        text = data.get('message', '').strip() if isinstance(data, dict) else str(data).strip()
        if not text:
            emit('error', {'message': 'Пустое сообщение'})
            return

        msg = Message(content=text, user_id=current_user.id)
        db.session.add(msg)
        db.session.commit()

        print(f"✅ Сохранено сообщение #{msg.id}")

        emit('new_message', {
            'id': msg.id,
            'text': msg.content,
            'username': current_user.username,
            'time': msg.timestamp.strftime('%H:%M'),
            'user_id': current_user.id
        }, broadcast=True)

    except Exception as e:
        print(f"❌ Ошибка отправки: {e}")
        db.session.rollback()
        emit('error', {'message': str(e)})


@socketio.on('request_edit')
def on_request_edit(data):
    try:
        message_id = data.get('message_id') if isinstance(data, dict) else data
        message = db.session.get(Message, message_id)

        if message and message.user_id == current_user.id:
            emit('edit_allowed', {'message_id': message.id, 'content': message.content})
        else:
            emit('edit_error', {'error': 'Нет прав'})
    except Exception as e:
        emit('edit_error', {'error': str(e)})


@socketio.on('request_delete')
def on_request_delete(data):
    try:
        message_id = data.get('message_id') if isinstance(data, dict) else data
        message = db.session.get(Message, message_id)

        if message and message.user_id == current_user.id:
            emit('delete_allowed', {'message_id': message.id})
        else:
            emit('delete_error', {'error': 'Нет прав'})
    except Exception as e:
        emit('delete_error', {'error': str(e)})


@app.errorhandler(404)
def not_found_error(error):
    return render_template('error.html', error='Страница не найдена', code=404), 404


@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('error.html', error='Внутренняя ошибка сервера', code=500), 500


@app.errorhandler(403)
def forbidden_error(error):
    return render_template('error.html', error='Доступ запрещён', code=403), 403


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        print("✅ База данных готова")

    print("\n" + "=" * 60)
    print("🚀 NEXUS MESSENGER ЗАПУЩЕН")
    print("=" * 60)
    print(f"📍 Локально: http://127.0.0.1:{PORT}")
    print(f"🌐 В сети:   http://0.0.0.0:{PORT}")
    print(f"📧 Почта:    " + app.config['MAIL_USERNAME'])
    print("=" * 60 + "\n")

    socketio.run(app, debug=True, host='0.0.0.0', port=PORT, allow_unsafe_werkzeug=True)