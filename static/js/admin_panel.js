document.addEventListener('DOMContentLoaded', function() {
    const adminCards = document.querySelectorAll('.admin-card');
    adminCards.forEach(function(card) {
        card.addEventListener('click', function(e) {
            const section = this.dataset.section;
            console.log('Переход в раздел:', section);
        });
    });

    const statCards = document.querySelectorAll('.stat-card');
    statCards.forEach(function(card) {
        card.addEventListener('click', function() {
            const stat = this.dataset.stat;
            const value = this.querySelector('.stat-value').textContent;
            console.log('Статистика:', stat, '=', value);
        });
    });

    const userRows = document.querySelectorAll('.user-row');
    userRows.forEach(function(row) {
        const link = row.querySelector('.username-link');
        if (link) {
            row.addEventListener('click', function(e) {
                if (!e.target.closest('a')) {
                    e.preventDefault();
                    window.location.href = link.href;
                }
            });
        }
    });

    const sectionTitle = document.querySelector('.section-title');
    if (sectionTitle) {
        sectionTitle.style.cursor = 'pointer';
        sectionTitle.addEventListener('click', function() {
            const usersList = document.querySelector('.users-list');
            if (!usersList) return;

            const rows = Array.from(usersList.querySelectorAll('.user-row'));
            rows.sort(function(a, b) {
                const dateA = new Date(a.dataset.userCreated);
                const dateB = new Date(b.dataset.userCreated);
                return dateB - dateA;
            });

            rows.forEach(function(row) {
                usersList.appendChild(row);
            });

            console.log('Список отсортирован по дате');
        });
    }

    const now = new Date();
    const oneDayAgo = new Date(now - 24 * 60 * 60 * 1000);

    userRows.forEach(function(row) {
        const created = new Date(row.dataset.userCreated);
        if (created > oneDayAgo) {
            row.classList.add('border-l-4', 'border-indigo-500');
            row.title = 'Новый пользователь (за последние 24ч)';
        }
    });
});