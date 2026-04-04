document.addEventListener('DOMContentLoaded', function() {
    const userId = document.querySelector('.user-card')?.dataset?.userId;

    const deleteForm = document.querySelector('.confirm-delete-form');
    if (deleteForm) {
        deleteForm.addEventListener('submit', function(e) {
            e.preventDefault();
            if (confirm('Вы уверены? Это действие необратимо!\n\nУдалить аккаунт пользователя?')) {
                this.submit();
            }
        });
    }

    const banForm = document.querySelector('.ban-form');
    if (banForm) {
        banForm.addEventListener('submit', function(e) {
            const reason = this.querySelector('.input-ban-reason')?.value?.trim();
            if (!reason && !confirm('Забанить без указания причины?')) {
                e.preventDefault();
            }
        });
    }

    const editForm = document.querySelector('.form-edit-user');
    if (editForm) {
        editForm.addEventListener('submit', function(e) {
            const username = editForm.querySelector('.input-username')?.value?.trim();
            const email = editForm.querySelector('.input-email')?.value?.trim();

            if (!username) {
                e.preventDefault();
                alert('Имя пользователя не может быть пустым');
                editForm.querySelector('.input-username')?.focus();
                return;
            }

            if (!email || !email.includes('@')) {
                e.preventDefault();
                alert('Введите корректный email');
                editForm.querySelector('.input-email')?.focus();
                return;
            }
        });
    }

    const messageItems = document.querySelectorAll('.message-item');
    messageItems.forEach(function(item) {
        item.addEventListener('click', function() {
            const content = this.querySelector('.message-content')?.textContent;
            if (content && content.includes('...')) {
                console.log('Полный текст сообщения:', content);
            }
        });
    });

    const now = new Date();
    const oneHourAgo = new Date(now - 60 * 60 * 1000);

    messageItems.forEach(function(item) {
        const timestamp = item.dataset.messageTime;
        if (timestamp) {
            const msgTime = new Date(timestamp);
            if (msgTime > oneHourAgo) {
                item.classList.add('border-l-4', 'border-indigo-500', 'bg-gray-700');
                item.title = 'Новое сообщение (за последний час)';
            }
        }
    });

    const firstInput = editForm?.querySelector('input:not([type="hidden"])');
    if (firstInput) {
        firstInput.focus();
    }

    let formChanged = false;
    if (editForm) {
        const inputs = editForm.querySelectorAll('input, textarea');
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

        editForm.addEventListener('submit', function() {
            formChanged = false;
        });
    }
});