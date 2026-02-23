from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_socketio import SocketIO, emit, join_room
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret-key-change-this-in-production'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///chat.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
socketio = SocketIO(app, cors_allowed_origins="*")
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


# --- Модели Базы Данных ---
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    username = db.Column(db.String(150), nullable=False)


class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref='messages')


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# --- Маршруты (Страницы) ---
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
            flash('Этот email уже зарегистрирован', 'error')
            return redirect(url_for('register'))

        new_user = User(
            email=email,
            username=username,
            password=generate_password_hash(password, method='pbkdf2:sha256')
        )
        db.session.add(new_user)
        db.session.commit()
        flash('Регистрация успешна! Теперь войдите.', 'success')
        return redirect(url_for('login'))
    return render_template('auth.html', mode='register')


@app.route('/chat')
@login_required
def chat():
    # Загружаем последние 50 сообщений
    messages = Message.query.order_by(Message.timestamp.desc()).limit(50).all()
    messages.reverse()  # Чтобы новые были внизу
    return render_template('chat.html', messages=messages)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


# --- SocketIO (Реальное время) ---
@socketio.on('send_message')
def handle_message(data):
    msg_content = data['message']
    if msg_content:
        # Сохраняем в БД
        new_msg = Message(content=msg_content, user_id=current_user.id)
        db.session.add(new_msg)
        db.session.commit()

        # Отправляем всем подключенным
        emit('receive_message', {
            'message': msg_content,
            'username': current_user.username,
            'time': new_msg.timestamp.strftime('%H:%M'),
            'is_mine': False  # Клиент сам решит, его ли это сообщение
        }, broadcast=True)


if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Создает базу данных при первом запуске
    # host='0.0.0.0' позволяет подключаться с других устройств в Wi-Fi
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)