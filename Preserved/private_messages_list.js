document.addEventListener('DOMContentLoaded', function() {
    const items = document.querySelectorAll('.conversation-item');

    items.forEach(function(item) {
        item.addEventListener('click', function(e) {
            const userId = this.dataset.userId;
            console.log('Открытие диалога с пользователем:', userId);
        });
    });

    const unreadBadges = document.querySelectorAll('.unread-badge');
    if (unreadBadges.length > 0) {
        console.log('Найдено непрочитанных:', unreadBadges.length);
    }
});