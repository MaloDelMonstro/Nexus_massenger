document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('verify-form');
    const codeInput = document.getElementById('code');

    if (codeInput) {
        codeInput.focus();
    }

    if (codeInput) {
        codeInput.addEventListener('input', function() {
            this.value = this.value.replace(/[^0-9]/g, '');

            if (this.value.length === 6 && form) {
                form.requestSubmit();
            }
        });

        codeInput.addEventListener('paste', function(e) {
            e.preventDefault();
            const pasted = (e.clipboardData || window.clipboardData).getData('text');
            const digits = pasted.replace(/[^0-9]/g, '').slice(0, 6);
            this.value = digits;

            if (digits.length === 6 && form) {
                form.requestSubmit();
            }
        });
    }

    const resendForm = document.querySelector('.resend-form');
    if (resendForm) {
        resendForm.addEventListener('submit', function(e) {
            if (!confirm('Отправить код ещё раз?')) {
                e.preventDefault();
            }
        });
    }

    if (codeInput && form) {
        codeInput.addEventListener('keydown', function(e) {
            if (e.key === 'Enter') {
                e.preventDefault();
                if (this.value.length === 6) {
                    form.requestSubmit();
                }
            }
        });
    }
});