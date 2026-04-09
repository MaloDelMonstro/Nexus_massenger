document.addEventListener('DOMContentLoaded', function() {
    const userId = document.body.dataset.userId;
    const username = document.body.dataset.username;

    console.log('Профиль загружен:', username);

    const statItems = document.querySelectorAll('.stat-item');
    statItems.forEach(function(item, index) {
        item.style.animationDelay = (index * 0.1) + 's';
    });

    const avatarContainer = document.querySelector('.profile-avatar-container');
    if (avatarContainer) {
        avatarContainer.addEventListener('click', function() {
            const avatar = this.querySelector('img');
            if (avatar) {
                console.log('Аватар:', avatar.src);
            }
        });
    }

    const userIdElements = document.querySelectorAll('.user-id-primary, .user-id-additional');
    userIdElements.forEach(function(el) {
        el.style.cursor = 'pointer';
        el.title = 'Нажмите, чтобы скопировать ID';

        el.addEventListener('click', function() {
            const id = this.textContent.trim().split('\n').pop().trim();
            navigator.clipboard.writeText(id).then(function() {
                const original = el.style.backgroundColor;
                el.style.backgroundColor = 'rgba(34, 197, 94, 0.2)';
                setTimeout(function() {
                    el.style.backgroundColor = original;
                }, 300);
            });
        });
    });
});