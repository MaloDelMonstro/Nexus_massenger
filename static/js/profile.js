document.addEventListener('DOMContentLoaded', function() {
    const avatarContainer = document.querySelector('.profile-avatar-container');
    if (avatarContainer) {
        avatarContainer.addEventListener('click', function() {
            console.log('Клик по аватару');
        });
    }

    const userIdElements = document.querySelectorAll('.user-id-primary, .user-id-additional');
    userIdElements.forEach(function(el) {
        el.addEventListener('click', function() {
            const text = this.textContent.trim();
            navigator.clipboard.writeText(text).then(function() {
                console.log('ID скопирован:', text);
            });
        });
    });

    document.querySelectorAll('a[href^="#"]').forEach(function(anchor) {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({ behavior: 'smooth' });
            }
        });
    });

    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            const backLink = document.querySelector('a[href="/chat"]');
            if (backLink) {
                backLink.click();
            }
        }
    });
});