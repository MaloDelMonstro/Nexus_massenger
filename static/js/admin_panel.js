document.addEventListener('DOMContentLoaded', function() {
    const cards = document.querySelectorAll('.admin-card');

    cards.forEach(function(card) {
        card.addEventListener('click', function(e) {
            const section = this.dataset.section;
            console.log('Переход в раздел:', section);
        });
    });
});