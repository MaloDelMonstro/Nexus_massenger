from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_socketio import SocketIO, emit
from flask_mail import Mail, Message as MailMessage
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta, timezone
import random

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-change-this'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///chat.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'void62166@gmail.com'
app.config['MAIL_PASSWORD'] = 'qohd cwrf dwst fcke '
app.config['MAIL_DEFAULT_SENDER'] = 'void62166@gmail.com'

db = SQLAlchemy(app)
socketio = SocketIO(app, cors_allowed_origins="*")
mail = Mail(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    username = db.Column(db.String(150), nullable=False)
    is_verified = db.Column(db.Boolean, default=False)  # Подтвержден ли email


class VerificationCode(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), nullable=False)
    code = db.Column(db.String(6), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=False)


class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
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
            sender=app.config['MAIL_DEFAULT_SENDER'],
            body=f'Ваш код подтверждения: {code}',
            html=f'<h1>Ваш код: {code}</h1>'
        )
        mail.send(msg)
        print(f"✅ Письмо отправлено на {email}")
        return True
    except Exception as e:
        print(f"❌ Ошибка: {e}")
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
            flash('Этот email уже зарегистрирован', 'error')
            return redirect(url_for('register'))

        new_user = User(
            email=email,
            username=username,
            password=generate_password_hash(password, method='pbkdf2:sha256'),
            is_verified=False
        )
        db.session.add(new_user)
        db.session.commit()

        # Генерируем и отправляем код
        code = generate_code()
        expires_at = datetime.now(timezone.utc) + timedelta(minutes=10)
        verification = VerificationCode(email=email, code=code, expires_at=expires_at)
        db.session.add(verification)
        db.session.commit()

        if send_verification_email(email, code):
            flash('Код подтверждения отправлен на почту', 'success')
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
            if datetime.utcnow() > verification.expires_at:
                flash('Код истек', 'error')
                db.session.delete(verification)
                db.session.commit()
                return redirect(url_for('register'))

            user = User.query.filter_by(email=email).first()
            user.is_verified = True
            db.session.delete(verification)
            db.session.commit()

            flash('Email подтвержден! Теперь войдите', 'success')
            return redirect(url_for('login'))
        else:
            flash('Неверный код', 'error')

    return render_template('verify.html', email=email)


@app.route('/resend-code', methods=['POST'])
def resend_code():
    email = request.form.get('email')
    user = User.query.filter_by(email=email).first()

    if not user or user.is_verified:
        flash('Ошибка отправки', 'error')
        return redirect(url_for('login'))

    VerificationCode.query.filter_by(email=email).delete()

    code = generate_code()
    expires_at = datetime.utcnow() + timedelta(minutes=10)
    verification = VerificationCode(email=email, code=code, expires_at=expires_at)
    db.session.add(verification)
    db.session.commit()

    if send_verification_email(email, code):
        flash('Новый код отправлен', 'success')
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


@socketio.on('send_message')
def handle_message(data):
    if not current_user.is_authenticated or not current_user.is_verified:
        return
    msg_content = data['message']
    if msg_content:
        new_msg = Message(content=msg_content, user_id=current_user.id)
        db.session.add(new_msg)
        db.session.commit()
        emit('receive_message', {
            'message': msg_content,
            'username': current_user.username,
            'time': new_msg.timestamp.strftime('%H:%M'),
            'user_id': current_user.id
        }, broadcast=True)


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    socketio.run(app, debug=True, host='0.0.0.0', port=8080, allow_unsafe_werkzeug=True)