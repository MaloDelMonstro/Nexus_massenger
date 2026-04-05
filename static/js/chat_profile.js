function refreshData() {
    if (confirm('Обновить данные страницы?')) {
        location.reload();
    }
}

document.addEventListener('DOMContentLoaded', function() {
    const cards = document.querySelectorAll('.chat-info-card, .top-users-card, .recent-messages-card');
    cards.forEach(function(card, index) {
        card.style.animation = `fadeIn 0.3s ease forwards ${index * 0.1}s`;
        card.style.opacity = '0';
    });
});