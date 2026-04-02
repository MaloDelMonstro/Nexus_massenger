function refreshData() {
    if (confirm('Обновить данные страницы?')) {
        location.reload();
    }
}

document.addEventListener('DOMContentLoaded', function() {
    const cards = document.querySelectorAll('.stat-card, .top-user-item, .recent-message-item');

    cards.forEach(function(card) {
        card.addEventListener('click', function() {
            console.log('Клик по элементу:', this.className);
        });
    });
});