document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('profile-form');
    const usernameInput = document.getElementById('username');
    const emailInput = document.getElementById('email');
    const currentPasswordInput = document.getElementById('current_password');
    const newPasswordInput = document.getElementById('new_password');
    const confirmPasswordInput = document.getElementById('confirm_password');
    const saveBtn = form?.querySelector('.btn-save');

    let profileChanged = false;
    let passwordChanged = false;

    const profileFields = [usernameInput, emailInput];
    const passwordFields = [currentPasswordInput, newPasswordInput, confirmPasswordInput];

    profileFields.forEach(function(input) {
        if (input) {
            input.addEventListener('input', function() {
                profileChanged = true;
                clearError(this);
            });
        }
    });

    passwordFields.forEach(function(input) {
        if (input) {
            input.addEventListener('input', function() {
                passwordChanged = true;
                clearError(this);
            });
        }
    });

    if (emailInput) {
        emailInput.addEventListener('blur', function() {
            validateEmail(this);
        });
    }

    if (usernameInput) {
        usernameInput.addEventListener('blur', function() {
            validateUsername(this);
        });
    }

    if (newPasswordInput && confirmPasswordInput) {
        confirmPasswordInput.addEventListener('blur', function() {
            validatePasswordMatch(newPasswordInput.value, this.value);
        });
        newPasswordInput.addEventListener('input', function() {
            if (confirmPasswordInput.value && confirmPasswordInput.value !== this.value) {
                showError(confirmPasswordInput, 'Пароли не совпадают');
            } else {
                clearError(confirmPasswordInput);
            }
        });
    }

    if (form) {
        form.addEventListener('submit', function(e) {
            let isValid = true;

            if (profileChanged) {
                if (usernameInput && !validateUsername(usernameInput)) isValid = false;
                if (emailInput && !validateEmail(emailInput)) isValid = false;
            }

            if (passwordChanged) {
                if (currentPasswordInput && !currentPasswordInput.value) {
                    showError(currentPasswordInput, 'Введите текущий пароль');
                    isValid = false;
                }
                if (newPasswordInput && newPasswordInput.value.length < 6) {
                    showError(newPasswordInput, 'Минимум 6 символов');
                    isValid = false;
                }
                if (!validatePasswordMatch(newPasswordInput?.value, confirmPasswordInput?.value)) {
                    isValid = false;
                }
            }

            if (!isValid) {
                e.preventDefault();
                const firstError = form.querySelector('.error-message:not(.hidden)');
                if (firstError) {
                    const input = firstError.closest('.form-group')?.querySelector('input');
                    input?.focus();
                }
                return;
            }

            if (saveBtn) {
                saveBtn.classList.add('loading');
                saveBtn.disabled = true;
            }
        });
    }

    window.addEventListener('beforeunload', function(e) {
        if (profileChanged || passwordChanged) {
            e.preventDefault();
            e.returnValue = '';
        }
    });

    function validateEmail(input) {
        if (!input.value) {
            showError(input, 'Email обязателен');
            return false;
        }
        if (!input.validity.valid) {
            showError(input, 'Введите корректный email');
            return false;
        }
        clearError(input);
        return true;
    }

    function validateUsername(input) {
        if (!input.value) {
            showError(input, 'Имя пользователя обязательно');
            return false;
        }
        if (input.value.length < 2) {
            showError(input, 'Минимум 2 символа');
            return false;
        }
        if (!/^[a-zA-Z0-9_\-\.]+$/.test(input.value)) {
            showError(input, 'Только буквы, цифры, _ - .');
            return false;
        }
        clearError(input);
        return true;
    }

    function validatePasswordMatch(pass1, pass2) {
        if (pass1 && pass2 && pass1 !== pass2) {
            showError(confirmPasswordInput, 'Пароли не совпадают');
            return false;
        }
        clearError(confirmPasswordInput);
        return true;
    }

    function showError(input, message) {
        const errorEl = input.closest('.form-group')?.querySelector('.error-message');
        if (errorEl) {
            errorEl.textContent = message;
            errorEl.classList.remove('hidden');
        }
        input.classList.add('border-red-500');
    }

    function clearError(input) {
        const errorEl = input.closest('.form-group')?.querySelector('.error-message');
        if (errorEl) {
            errorEl.textContent = '';
            errorEl.classList.add('hidden');
        }
        input.classList.remove('border-red-500');
    }

    if (usernameInput) {
        setTimeout(() => usernameInput.focus(), 100);
    }
});