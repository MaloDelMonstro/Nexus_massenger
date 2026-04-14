from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_user, current_user, login_required
from services.auth_service import (register_user_and_send_verification,
                                   verify_email_code,
                                   regenerate_verification_code,
                                   get_verification_status)

from services.user_service import authenticate_user

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('chat.chat'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')

        user = authenticate_user(email, password)

        if user:
            login_user(user)
            flash('Вход выполнен', 'success')
            return redirect(url_for('chat.chat'))
        else:
            flash('Неверный email или пароль', 'error')

    return render_template('auth.html', mode='login')


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('chat.chat'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        region = request.form.get('region', '1')

        user, errors = register_user_and_send_verification(
            email=email,
            username=username,
            password=password,
            region=int(region)
        )

        if errors:
            for error in errors:
                flash(error, 'error')
            return redirect(url_for('auth.register'))


        flash('Код подтверждения отправлен', 'success')
        return redirect(url_for('auth.verify_email', email=email))

    return render_template('auth.html', mode='register')


@auth_bp.route('/verify_email/<email>')
@login_required
def verify_email(email):
    if current_user.email != email:
        flash('Доступ запрещён', 'error')
        return redirect(url_for('chat.chat'))
    return render_template('verify_email.html', email=email)


@auth_bp.route('/verify_code', methods=['POST'])
@login_required
def verify_code():
    email = request.form.get('email')
    code = request.form.get('code')

    if current_user.email != email:
        return jsonify({'success': False, 'error': 'Доступ запрещён'}), 403

    success, message = verify_email_code(email, code)

    if success:
        return jsonify({
            'success': True,
            'redirect': url_for('chat.chat')
        })
    else:
        return jsonify({'success': False, 'error': message}), 400


@auth_bp.route('/resend-code', methods=['POST'])
@login_required
def resend_verification_code():
    email = current_user.email

    success, message = regenerate_verification_code(email)

    if success:
        return jsonify({'success': True})
    else:
        return jsonify({'success': False, 'error': message}), 400


@auth_bp.route('/logout')
def logout():
    from flask_login import logout_user
    logout_user()
    return redirect(url_for('auth.login'))
