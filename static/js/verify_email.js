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
        form.addEventListener('submit', async function(e) {
            e.preventDefault();

            const code = codeInput?.value?.trim();
            const email = document.querySelector('input[name="email"]').value;

            if (!code || code.length !== 6 || !/^[0-9]{6}$/.test(code)) {
                showError(codeInput, 'Введите 6-значный код');
                return;
            }

            if (verifyBtn) {
                verifyBtn.classList.add('loading');
                verifyBtn.disabled = true;
            }

            try {
                const response = await fetch('/verify_code', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    credentials: 'same-origin',
                    body: JSON.stringify({ email, code })
                });

                const data = await response.json();

                if (data.success) {
                    // ✅ Перенаправляем в чат
                    if (data.redirect) {
                        window.location.href = data.redirect;
                    } else {
                        // Если redirect нет — просто показываем сообщение
                        alert('Email подтверждён!');
                    }
                } else {
                    showError(codeInput, data.error || 'Неверный код');
                }
            } catch (err) {
                console.error('Ошибка:', err);
                showError(codeInput, 'Сеть недоступна');
            } finally {
                if (verifyBtn) {
                    verifyBtn.classList.remove('loading');
                    verifyBtn.disabled = false;
                }
            }
        });
    }

    if (resendForm) {
        resendForm.addEventListener('submit', async function(e) {
            e.preventDefault();

            const btn = this.querySelector('.btn-resend');
            const email = document.querySelector('input[name="email"]').value;

            if (btn) {
                const originalText = btn.textContent;
                btn.textContent = 'Отправляем...';
                btn.disabled = true;

                try {
                    const response = await fetch('/resend-code', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        credentials: 'same-origin',
                        body: JSON.stringify({ email })
                    });

                    const data = await response.json();

                    if (data.success) {
                        alert('Код отправлен повторно');
                    } else {
                        alert('Ошибка: ' + (data.error || 'Неизвестная ошибка'));
                    }
                } catch (err) {
                    console.error('Ошибка:', err);
                    alert('Ошибка сети');
                } finally {
                    btn.textContent = originalText;
                    btn.disabled = false;
                }
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

