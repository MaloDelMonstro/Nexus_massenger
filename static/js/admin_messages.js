document.addEventListener('DOMContentLoaded', function() {
    const deleteForms = document.querySelectorAll('.delete-form');
    const messageItems = document.querySelectorAll('.message-item');

    deleteForms.forEach(function(form) {
        form.addEventListener('submit', function(e) {
            if (!confirm('Удалить это сообщение?')) {
                e.preventDefault();
                return;
            }

            const messageItem = this.closest('.message-item');
            if (messageItem) {
                e.preventDefault();

                messageItem.classList.add('message-deleting');

                setTimeout(function() {
                    form.submit();
                }, 300);
            }
        });
    });

    messageItems.forEach(function(item) {
        const timeEl = item.querySelector('.message-time');
        if (timeEl) {
            timeEl.addEventListener('mouseenter', function() {
                item.style.backgroundColor = '#374151';
            });
            timeEl.addEventListener('mouseleave', function() {
                item.style.backgroundColor = '';
            });
        }
    });

    const usernameLinks = document.querySelectorAll('.username-link');
    usernameLinks.forEach(function(link) {
        link.addEventListener('click', function(e) {
        });
    });
});