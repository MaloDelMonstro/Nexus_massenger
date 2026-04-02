document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('profile-form');
    const newPassword = document.getElementById('new_password');
    const confirmPassword = document.getElementById('confirm_password');
    const currentPassword = document.getElementById('current_password');

    if (form) {
        form.addEventListener('submit', function(e) {
            const newPass = newPassword?.value || '';
            const confirmPass = confirmPassword?.value || '';
            const currPass = currentPassword?.value || '';

            if (newPass || confirmPass) {
                if (!currPass) {
                    e.preventDefault();
                    alert('Введите текущий пароль для смены');
                    currentPassword?.focus();
                    return;
                }
                if (newPass.length < 6) {
                    e.preventDefault();
                    alert('Новый пароль должен быть не менее 6 символов');
                    newPassword?.focus();
                    return;
                }
                if (newPass !== confirmPass) {
                    e.preventDefault();
                    alert('Пароли не совпадают');
                    confirmPassword?.focus();
                    return;
                }
            }

            const emailInput = document.getElementById('email');
            if (emailInput) {
                emailInput.value = emailInput.value.trim();
            }
        });
    }

    [newPassword, confirmPassword].forEach(function(input) {
        if (input) {
            input.addEventListener('input', function() {
                if (confirmPassword?.value && newPassword?.value) {
                    if (confirmPassword.value !== newPassword.value) {
                        confirmPassword.style.borderColor = '#ef4444';
                    } else {
                        confirmPassword.style.borderColor = '';
                    }
                }
            });
        }
    });

    const firstInput = document.getElementById('username');
    if (firstInput) {
        firstInput.focus();
    }

    let formChanged = false;
    const inputs = form?.querySelectorAll('input') || [];
    inputs.forEach(function(input) {
        input.addEventListener('input', function() {
            formChanged = true;
        });
    });

    window.addEventListener('beforeunload', function(e) {
        if (formChanged) {
            e.preventDefault();
            e.returnValue = '';
        }
    });

    const cancelBtn = document.querySelector('.btn-cancel');
    if (cancelBtn) {
        cancelBtn.addEventListener('click', function() {
            formChanged = false;
        });
    }
});