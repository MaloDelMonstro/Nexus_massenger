document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('verify-form');
    const codeInput = document.getElementById('code');
    const resendForm = document.querySelector('.resend-form');
    const verifyBtn = form?.querySelector('.btn-verify');

    if (codeInput) {
        setTimeout(() => codeInput.focus(), 100);

        codeInput.addEventListener('input', function() {
            this.value = this.value.replace(/[^0-9]/g, '');

            const errorEl = this.closest('.form-group')?.querySelector('.error-message');
            if (errorEl && this.value.length > 0) {
                errorEl.classList.add('hidden');
                errorEl.textContent = '';
            }

            if (this.value.length === 6 && form) {
                form.requestSubmit();
            }
        });

        codeInput.addEventListener('blur', function() {
            if (this.value && this.value.length !== 6) {
                showError(this, 'Код должен содержать 6 цифр');
            }
        });
    }

    if (form) {
        form.addEventListener('submit', function(e) {
            const code = codeInput?.value?.trim();

            if (!code || code.length !== 6) {
                e.preventDefault();
                showError(codeInput, 'Введите 6-значный код');
                return;
            }

            if (!/^[0-9]{6}$/.test(code)) {
                e.preventDefault();
                showError(codeInput, 'Только цифры');
                return;
            }

            if (verifyBtn) {
                verifyBtn.classList.add('loading');
                verifyBtn.disabled = true;
            }
        });
    }

    if (resendForm) {
        resendForm.addEventListener('submit', function(e) {
            const btn = this.querySelector('.btn-resend');
            if (btn) {
                const originalText = btn.textContent;
                btn.textContent = 'Отправляем...';
                btn.disabled = true;

                setTimeout(() => {
                    btn.textContent = originalText;
                    btn.disabled = false;
                }, 3000);
            }
        });
    }

    function showError(input, message) {
        const errorEl = input?.closest('.form-group')?.querySelector('.error-message');
        if (errorEl) {
            errorEl.textContent = message;
            errorEl.classList.remove('hidden');
        }
        input?.classList.add('border-red-500');
    }

    if (codeInput && 'OTPCredential' in window) {
        if ('credentials' in navigator) {
            navigator.credentials.get({
                otp: { transport: ['email'] },
                signal: AbortSignal.timeout(30000)
            }).then(otp => {
                if (otp?.code) {
                    codeInput.value = otp.code;
                    form?.requestSubmit();
                }
            }).catch(err => {
                console.log('WebOTP не доступен:', err);
            });
        }
    }
});