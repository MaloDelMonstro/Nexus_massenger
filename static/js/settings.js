function showTab(tabName) {
    document.querySelectorAll('.tab-content').forEach(function(tab) {
        tab.classList.add('hidden');
    });

    document.querySelectorAll('.tab-btn').forEach(function(btn) {
        btn.classList.remove('border-indigo-500', 'text-indigo-400');
        btn.classList.add('border-transparent');
    });

    document.getElementById('tab-' + tabName).classList.remove('hidden');

    const activeBtn = document.querySelector('[data-tab="' + tabName + '"]');
    if (activeBtn) {
        activeBtn.classList.remove('border-transparent');
        activeBtn.classList.add('border-indigo-500', 'text-indigo-400');
    }
}

function resetAvatar() {
    const input = document.querySelector('.input-avatar-url');
    if (input) {
        input.value = '';
        input.form.submit();
    }
}

function logoutAll() {
    if (confirm('Выйти из всех устройств кроме текущего?')) {
        fetch('/settings/logout-all', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            }
        })
        .then(function(response) { return response.json(); })
        .then(function(data) {
            alert('Вы вышли из всех устройств кроме текущего');
        })
        .catch(function(error) {
            console.error('Error:', error);
            alert('Ошибка при выходе');
        });
    }
}

function confirmDelete() {
    return confirm('Вы уверены? Это действие необратимо!');
}

document.addEventListener('DOMContentLoaded', function() {
    showTab('profile');

    const passwordForm = document.querySelector('.password-form');
    if (passwordForm) {
        passwordForm.addEventListener('submit', function(e) {
            const newPass = document.getElementById('new_password')?.value || '';
            const confirmPass = document.getElementById('confirm_password')?.value || '';
            const currPass = document.getElementById('current_password')?.value || '';

            if (newPass || confirmPass) {
                if (!currPass) {
                    e.preventDefault();
                    alert('Введите текущий пароль для смены');
                    document.getElementById('current_password')?.focus();
                    return;
                }
                if (newPass.length < 6) {
                    e.preventDefault();
                    alert('Новый пароль должен быть не менее 6 символов');
                    document.getElementById('new_password')?.focus();
                    return;
                }
                if (newPass !== confirmPass) {
                    e.preventDefault();
                    alert('Пароли не совпадают');
                    document.getElementById('confirm_password')?.focus();
                    return;
                }
            }
        });
    }

    const profileForm = document.querySelector('.profile-form');
    if (profileForm) {
        profileForm.addEventListener('submit', function(e) {
            const email = document.getElementById('email')?.value || '';
            if (email) {
                document.getElementById('email').value = email.trim();
            }
        });
    }

    const newPassInput = document.getElementById('new_password');
    const confirmPassInput = document.getElementById('confirm_password');

    if (newPassInput && confirmPassInput) {
        confirmPassInput.addEventListener('input', function() {
            if (newPassInput.value && confirmPassInput.value) {
                if (newPassInput.value !== confirmPassInput.value) {
                    confirmPassInput.style.borderColor = '#ef4444';
                } else {
                    confirmPassInput.style.borderColor = '';
                }
            }
        });
    }

    const activeTab = document.querySelector('.tab-content:not(.hidden)');
    if (activeTab) {
        const firstInput = activeTab.querySelector('input:not([type="checkbox"]):not([type="radio"])');
        if (firstInput) {
            firstInput.focus();
        }
    }
});