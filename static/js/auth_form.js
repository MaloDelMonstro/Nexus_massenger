document.addEventListener('DOMContentLoaded', function() {
    const form = document.querySelector('.auth-form');
    const passwordInput = document.querySelector('.input-password');
    const emailInput = document.querySelector('.input-email');

    if (passwordInput) {
        passwordInput.addEventListener('input', function() {
            if (this.value.length > 0 && this.value.length < 6) {
                this.style.borderColor = '#ef4444';
            } else {
                this.style.borderColor = '';
            }
        });
    }

    if (form && emailInput) {
        form.addEventListener('submit', function() {
            emailInput.value = emailInput.value.trim();
        });
    }

    const firstInput = document.querySelector('.input-username, .input-email');
    if (firstInput) {
        firstInput.focus();
    }
});