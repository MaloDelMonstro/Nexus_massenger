document.addEventListener('DOMContentLoaded', function() {
    const form = document.querySelector('.admin-form');
    const nameInput = document.getElementById('chat_name');
    const descInput = document.getElementById('chat_description');
    const avatarInput = document.getElementById('chat_avatar');
    const previewName = document.querySelector('.preview-name');
    const previewDesc = document.querySelector('.preview-description');
    const previewAvatar = document.querySelector('.avatar-preview img');

    if (nameInput && previewName) {
        nameInput.addEventListener('input', function() {
            previewName.textContent = this.value || 'Название чата';
        });
    }

    if (descInput && previewDesc) {
        descInput.addEventListener('input', function() {
            previewDesc.textContent = this.value || 'Описание чата';
        });
    }

    if (avatarInput && previewAvatar) {
        avatarInput.addEventListener('input', function() {
            const url = this.value.trim();
            if (url && (url.startsWith('http://') || url.startsWith('https://'))) {
                previewAvatar.src = url;
                previewAvatar.style.display = 'block';
                previewAvatar.nextElementSibling?.style?.display?.('none');
            } else {
                previewAvatar.style.display = 'none';
            }
        });
    }

    if (form) {
        form.addEventListener('submit', function(e) {
            const name = nameInput?.value?.trim();
            if (!name) {
                e.preventDefault();
                alert('Введите название чата');
                nameInput?.focus();
            }
        });
    }
});