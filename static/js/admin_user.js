document.addEventListener('DOMContentLoaded', function() {
    const deleteForm = document.querySelector('.confirm-delete-form');
    if (deleteForm) {
        deleteForm.addEventListener('submit', function(e) {
            const username = deleteForm.querySelector('button').textContent;
            if (!confirm('Удалить этого пользователя? Это действие необратимо!')) {
                e.preventDefault();
            }
        });
    }

    const banForm = document.querySelector('.btn-ban');
    if (banForm) {
        banForm.closest('form').addEventListener('submit', function(e) {
            const reason = this.querySelector('.input-ban-reason').value;
            if (!reason && !confirm('Забанить без указания причины?')) {
                e.preventDefault();
            }
        });
    }

    const editForm = document.querySelector('.form-edit-user');
    if (editForm) {
        editForm.addEventListener('submit', function(e) {
            const username = editForm.querySelector('.input-username').value;
            const email = editForm.querySelector('.input-email').value;

            if (!username || !email) {
                e.preventDefault();
                alert('Заполните все обязательные поля');
            }
        });
    }
});