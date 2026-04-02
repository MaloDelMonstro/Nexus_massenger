document.addEventListener('DOMContentLoaded', function() {
    const userCards = document.querySelectorAll('.user-card');

    userCards.forEach(function(card) {
        card.addEventListener('click', function(e) {
            const userId = this.dataset.userId;
            console.log('Переход к пользователю:', userId);
        });
    });
});