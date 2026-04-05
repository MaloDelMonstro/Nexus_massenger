window.showTab = function(tabName) {
    document.querySelectorAll('.tab-content').forEach(function(tab) {
        tab.classList.add('hidden');
        tab.setAttribute('aria-hidden', 'true');
    });

    document.querySelectorAll('.tab-btn').forEach(function(btn) {
        btn.classList.remove('border-indigo-500', 'text-indigo-400');
        btn.classList.add('border-transparent', 'hover:text-gray-300');
        btn.setAttribute('aria-selected', 'false');
    });

    const targetTab = document.getElementById('tab-' + tabName);
    const targetBtn = document.getElementById('tab-btn-' + tabName);

    if (targetTab) {
        targetTab.classList.remove('hidden');
        targetTab.setAttribute('aria-hidden', 'false');
    }
    if (targetBtn) {
        targetBtn.classList.add('border-indigo-500', 'text-indigo-400');
        targetBtn.classList.remove('border-transparent', 'hover:text-gray-300');
        targetBtn.setAttribute('aria-selected', 'true');
    }

    localStorage.setItem('settingsTab', tabName);
};

window.resetAvatar = function() {
    if (confirm('Сбросить аватар на стандартный?')) {
        const form = document.querySelector('.avatar-form');
        const input = form?.querySelector('.input-avatar-url');
        if (input) {
            input.value = '';
            form.requestSubmit();
        }
    }
};

window.logoutAll = function() {
    if (confirm('Выйти со всех устройств кроме текущего?')) {
        alert('Функция будет доступна в следующем обновлении');
    }
};

window.confirmDelete = function() {
    return confirm('Вы уверены? Это действие НЕЛЬЗЯ отменить!\n\nВсе ваши данные будут удалены навсегда.');
};

document.addEventListener('DOMContentLoaded', function() {
    const savedTab = localStorage.getItem('settingsTab') || 'profile';
    showTab(savedTab);

    const forms = document.querySelectorAll('[data-form]');
    forms.forEach(function(form) {
        form.addEventListener('submit', function(e) {
            const formData = new FormData(form);
            let isValid = true;

            form.querySelectorAll('input[required]').forEach(function(input) {
                if (!input.value.trim()) {
                    isValid = false;
                    input.classList.add('border-red-500');
                    const errorEl = input.closest('.form-group')?.querySelector('.error-message');
                    if (errorEl) {
                        errorEl.textContent = 'Это поле обязательно';
                        errorEl.classList.remove('hidden');
                    }
                } else {
                    input.classList.remove('border-red-500');
                }
            });

            if (!isValid) {
                e.preventDefault();
            }
        });
    });

    document.querySelectorAll('input').forEach(function(input) {
        input.addEventListener('input', function() {
            this.classList.remove('border-red-500');
            const errorEl = this.closest('.form-group')?.querySelector('.error-message');
            if (errorEl) {
                errorEl.classList.add('hidden');
            }
        });
    });
});