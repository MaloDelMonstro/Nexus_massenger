document.addEventListener('DOMContentLoaded', function () {
    const container = document.querySelector('.error-container');
    const errorCode = container?.dataset?.errorCode;

    if (errorCode) {
        console.log(`Ошибка ${errorCode} загружена`);
        fetch('/api/log-error', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({code: errorCode, url: window.location.href})
        });
    }

    const buttons = document.querySelectorAll('.btn-back-chat, .btn-home');
    buttons.forEach(function (btn) {
        btn.addEventListener('mouseenter', function () {
            this.style.transform = 'translateY(-2px)';
        });
        btn.addEventListener('mouseleave', function () {
            this.style.transform = 'translateY(0)';
        });
    });

    buttons.forEach(function (btn) {
        btn.addEventListener('keydown', function (e) {
            if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                this.click();
            }
        });
    });
});