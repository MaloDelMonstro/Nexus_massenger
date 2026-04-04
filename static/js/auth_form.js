document.addEventListener('DOMContentLoaded', function() {
    const form = document.querySelector('.auth-form');
    const mode = document.querySelector('.auth-container')?.dataset?.mode;
    const passwordInput = document.getElementById('password');
    const emailInput = document.getElementById('email');
    const usernameInput = document.getElementById('username');

    const togglePasswordBtn = document.querySelector('.toggle-password');
    if (togglePasswordBtn && passwordInput) {
        togglePasswordBtn.addEventListener('click', function() {
            const isPassword = passwordInput.type === 'password';
            passwordInput.type = isPassword ? 'text' : 'password';
            this.setAttribute('aria-pressed', isPassword);
            this.setAttribute('title', isPassword ? 'Скрыть пароль' : 'Показать пароль');
            this.setAttribute('aria-label', isPassword ? 'Скрыть пароль' : 'Показать пароль');
        });
    }

    if (emailInput) {
        emailInput.addEventListener('blur', function() {
            validateEmail(this);
        });
        emailInput.addEventListener('input', function() {
            const errorEl = this.closest('.form-group')?.querySelector('.error-message');
            if (errorEl && this.validity.valid) {
                errorEl.classList.add('hidden');
                errorEl.textContent = '';
            }
        });
    }

    if (usernameInput && mode === 'register') {
        usernameInput.addEventListener('blur', function() {
            validateUsername(this);
        });
        usernameInput.addEventListener('input', function() {
            const errorEl = this.closest('.form-group')?.querySelector('.error-message');
            if (errorEl && this.validity.valid) {
                errorEl.classList.add('hidden');
                errorEl.textContent = '';
            }
        });
    }

    if (passwordInput) {
        passwordInput.addEventListener('blur', function() {
            validatePassword(this);
        });
        passwordInput.addEventListener('input', function() {
            const errorEl = this.closest('.form-group')?.querySelector('.error-message');
            if (errorEl && this.value.length >= 6) {
                errorEl.classList.add('hidden');
                errorEl.textContent = '';
            }
        });
    }

    if (form) {
        form.addEventListener('submit', function(e) {
            let isValid = true;

            if (usernameInput && mode === 'register') {
                isValid = validateUsername(usernameInput) && isValid;
            }
            if (emailInput) {
                isValid = validateEmail(emailInput) && isValid;
            }
            if (passwordInput) {
                isValid = validatePassword(passwordInput) && isValid;
            }

            if (!isValid) {
                e.preventDefault();
                const firstError = form.querySelector('.error-message:not(.hidden)');
                if (firstError) {
                    const input = firstError.closest('.form-group')?.querySelector('input, select');
                    input?.focus();
                }
                return;
            }

            const submitBtn = form.querySelector('.btn-submit');
            if (submitBtn) {
                submitBtn.classList.add('loading');
                submitBtn.disabled = true;
            }
        });
    }

    const firstInput = form?.querySelector('input:not([type="hidden"])');
    if (firstInput) {
        setTimeout(() => firstInput.focus(), 100);
    }

    function validateEmail(input) {
        const errorEl = input.closest('.form-group')?.querySelector('.error-message');
        if (!errorEl) return true;

        if (!input.value) {
            showError(errorEl, 'Email обязателен');
            return false;
        }
        if (!input.validity.valid) {
            showError(errorEl, 'Введите корректный email');
            return false;
        }
        errorEl.classList.add('hidden');
        errorEl.textContent = '';
        return true;
    }

    function validateUsername(input) {
        const errorEl = input.closest('.form-group')?.querySelector('.error-message');
        if (!errorEl) return true;

        if (!input.value) {
            showError(errorEl, 'Имя пользователя обязательно');
            return false;
        }
        if (input.value.length < 2) {
            showError(errorEl, 'Минимум 2 символа');
            return false;
        }
        if (!/^[a-zA-Z0-9_\-\.]+$/.test(input.value)) {
            showError(errorEl, 'Только буквы, цифры, _ - .');
            return false;
        }
        errorEl.classList.add('hidden');
        errorEl.textContent = '';
        return true;
    }

    function validatePassword(input) {
        const errorEl = input.closest('.form-group')?.querySelector('.error-message');
        if (!errorEl) return true;

        if (!input.value) {
            showError(errorEl, 'Пароль обязателен');
            return false;
        }
        if (input.value.length < 6) {
            showError(errorEl, 'Минимум 6 символов');
            return false;
        }
        errorEl.classList.add('hidden');
        errorEl.textContent = '';
        return true;
    }

    function showError(element, message) {
        element.textContent = message;
        element.classList.remove('hidden');
    }
});