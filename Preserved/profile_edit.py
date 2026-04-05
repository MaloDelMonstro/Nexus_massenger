"""@profile_bp.route('/edit', methods=['GET', 'POST'])
@login_required
def edit_profile() -> Response | str:
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
        flash('Профиль обновлён', 'success')
        return redirect(url_for('profile.profile'))

    return render_template('profile_edit.html', user=current_user)"""