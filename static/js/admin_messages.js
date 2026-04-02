document.addEventListener('DOMContentLoaded', function() {
    const forms = document.querySelectorAll('.delete-form');

    forms.forEach(function(form) {
        form.addEventListener('submit', function(e) {
            if (!confirm('Удалить это сообщение?')) {
                e.preventDefault();
            }
        });
    });
});