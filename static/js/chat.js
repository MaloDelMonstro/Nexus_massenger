const socket = io();

const currentUserId = window.currentUserId || parseInt(document.body.dataset.currentUserId, 10) || 0;

const sidebar = document.getElementById('sidebar');
const overlay = document.getElementById('overlay');
const messagesContainer = document.getElementById('messages-container');
const chatForm = document.getElementById('chat-form');
const messageInput = document.getElementById('message-input');
const chatSearch = document.getElementById('chat-search');
const toastContainer = document.getElementById('toast-container');

let pendingImageUrl = null;

window.handleFileSelect = function(input) {
    const file = input.files[0];
    if (!file) return;
    if (!file.type.startsWith('image/')) {
        showToast('Только изображения!', 'error');
        input.value = '';
        return;
    }

    const reader = new FileReader();
    reader.onload = (e) => {
        const previewImg = document.getElementById('preview-img');
        const previewBox = document.getElementById('image-preview-box');
        if (previewImg && previewBox) {
            previewImg.src = e.target.result;
            previewBox.classList.remove('hidden');
            document.getElementById('url-input-container').classList.add('hidden');
        }
        pendingImageUrl = e.target.result;
    };
    reader.readAsDataURL(file);
};

window.toggleUrlInput = function() {
    const urlContainer = document.getElementById('url-input-container');
    const urlField = document.getElementById('image-url-field');
    if (urlContainer && urlField) {
        urlContainer.classList.toggle('hidden');
        if (!urlContainer.classList.contains('hidden')) {
            urlField.focus();
            urlField.value = '';
            clearImageSelection();
        }
    }
};

window.clearImageSelection = function() {
    pendingImageUrl = null;
    const imageUpload = document.getElementById('image-upload');
    const urlField = document.getElementById('image-url-field');
    const urlContainer = document.getElementById('url-input-container');
    const previewBox = document.getElementById('image-preview-box');
    if (imageUpload) imageUpload.value = '';
    if (urlField) urlField.value = '';
    if (urlContainer) urlContainer.classList.add('hidden');
    if (previewBox) previewBox.classList.add('hidden');
    if (document.getElementById('preview-img')) document.getElementById('preview-img').src = '';
};

window.toggleSidebar = function () {
    if (!sidebar || !overlay) return;

    const isOpen = sidebar.classList.toggle('open');
    overlay.classList.toggle('active');

    if (window.innerWidth < 768) {
        sidebar.style.display = isOpen ? 'flex' : 'none';
    }
};

window.editMessage = function (messageId) {
    if (socket.connected) {
        socket.emit('request_edit', {message_id: messageId});
    } else {
        showToast('Нет соединения с сервером', 'error');
    }
};

window.deleteMessage = function (messageId) {
    if (confirm('Удалить сообщение?')) {
        if (socket.connected) {
            socket.emit('request_delete', {message_id: messageId});
        } else {
            showToast('Нет соединения с сервером', 'error');
        }
    }
};

socket.on('connect', function () {
    console.log('Подключено к серверу');
});

socket.on('disconnect', function () {
    console.log('Отключено');
    showToast('Потеря связи', 'error');
});

socket.on('new_message', function(data) {
    console.log('new_message получено:', data);

    if (!data || (!data.text && !data.image_url)) {
        console.error('Неверные данные:', data);
        return;
    }

    addMessageToDOM(
        data.text, data.username, data.time,
        data.id, data.user_id, data.user_new_id, data.user_avatar, data.bot_id,
        data.image_url
    );
});

socket.on('message_edited', function (data) {
    const el = document.querySelector(`[data-message-id="${data.message_id}"] .message-content`);
    if (el) {
        el.innerHTML = escapeHtml(data.content) + ' <span class="text-xs text-gray-400">(изм.)</span>';
        showToast('Сообщение изменено', 'success');
    }
});

socket.on('message_deleted', function (data) {
    const el = document.querySelector(`[data-message-id="${data.message_id}"]`);
    if (el) {
        el.classList.add('message-deleting');
        setTimeout(() => el.remove(), 300);
        showToast('Сообщение удалено', 'success');
    }
});

socket.on('edit_allowed', function (data) {
    const newText = prompt('Редактировать сообщение:', data.content);
    if (newText && newText.trim()) {
        fetch(`/message/${data.message_id}/edit`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            credentials: 'same-origin',
            body: JSON.stringify({content: newText.trim()})
        })
            .then(r => r.json())
            .then(d => {
                if (d.error) showToast('Ошибка: ' + d.error, 'error');
                else showToast('Изменено', 'success');
            })
            .catch(e => showToast('Ошибка: ' + e, 'error'));
    }
});

socket.on('delete_allowed', function (data) {
    fetch(`/message/${data.message_id}/delete`, {
        method: 'POST',
        credentials: 'same-origin'
    })
        .then(r => r.json())
        .then(d => {
            if (d.error) showToast('Ошибка: ' + d.error, 'error');
            else showToast('Удалено', 'success');
        })
        .catch(e => showToast('Ошибка: ' + e, 'error'));
});

socket.on('error', function (data) {
    showToast('Ошибка: ' + data.message, 'error');
});

if (chatForm && messageInput) {
    chatForm.addEventListener('submit', function (e) {
        e.preventDefault();
        const message = messageInput.value.trim();

        if (!message && !pendingImageUrl) {
            showToast('Введите сообщение или прикрепите изображение', 'error');
            return;
        }

        if (!socket.connected) {
            showToast('Нет соединения с сервером', 'error');
            return;
        }

        const sendData = { message: message };

        if (pendingImageUrl) {
            if (pendingImageUrl.startsWith('data:image')) {
                const blob = dataURLtoBlob(pendingImageUrl);
                const formData = new FormData();
                formData.append('image', blob, 'temp_image.jpg');

                fetch('/chat/upload-image', {
                    method: 'POST',
                    body: formData
                })
                .then(response => response.json())
                .then(result => {
                    if (result.url) {
                        sendData.image_url = result.url;
                        socket.emit('send_message', sendData);
                        messageInput.value = '';
                        clearImageSelection();
                        messageInput.style.height = 'auto';
                        messageInput.focus();
                    } else {
                        showToast('Ошибка загрузки изображения: ' + result.error, 'error');
                    }
                })
                .catch(error => {
                    console.error('Ошибка загрузки:', error);
                    showToast('Ошибка загрузки изображения', 'error');
                });
            } else {
                sendData.image_url = pendingImageUrl;
                socket.emit('send_message', sendData);
                messageInput.value = '';
                clearImageSelection();
                messageInput.style.height = 'auto';
                messageInput.focus();
            }
        } else {
            socket.emit('send_message', sendData);
            messageInput.value = '';
            clearImageSelection();
            messageInput.style.height = 'auto';
            messageInput.focus();
        }
    });

    messageInput.addEventListener('keydown', function (e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            chatForm.requestSubmit();
        }
    });

    messageInput.addEventListener('input', function () {
        this.style.height = 'auto';
        this.style.height = Math.min(this.scrollHeight, 150) + 'px';
    });
}

function dataURLtoBlob(dataurl) {
    let arr = dataurl.split(','), mime = arr[0].match(/:(.*?);/)[1],
        bstr = atob(arr[1]), n = bstr.length, u8arr = new Uint8Array(n);
    while(n--){
        u8arr[n] = bstr.charCodeAt(n);
    }
    return new Blob([u8arr], {type:mime});
}

if (chatSearch) {
    chatSearch.addEventListener('input', function (e) {
        const query = e.target.value.toLowerCase();
        document.querySelectorAll('.chat-item').forEach(item => {
            const text = item.textContent.toLowerCase();
            item.style.display = text.includes(query) ? 'block' : 'none';
        });
    });
}

document.addEventListener('DOMContentLoaded', function () {
    if (messagesContainer) {
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }
});

function showToast(message, type = 'info') {
    if (!toastContainer) return;
    const toast = document.createElement('div');
    toast.className = `toast-enter px-4 py-2 rounded-lg shadow-lg text-sm font-medium pointer-events-auto ${
        type === 'success' ? 'bg-green-600 text-white' :
            type === 'error' ? 'bg-red-600 text-white' :
                'bg-gray-700 text-white'
    }`;
    toast.textContent = message;
    toastContainer.appendChild(toast);
    setTimeout(() => {
        toast.classList.add('toast-exit');
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML.replace(/\n/g, '<br>');
}

function addMessageToDOM(content, username, time, messageId, userId, userNewId, userAvatar, botId = 0, imageUrl = null) {
    const isMine = userId === currentUserId;
    const isBot = userId === 0 || userNewId === 'BOT';
    const container = document.getElementById('messages-container');
    if (!container) return;

    const msgDiv = document.createElement('div');

    if (isBot) {
        msgDiv.className = 'flex justify-center message-group message-enter';
    } else {
        msgDiv.className = `flex ${isMine ? 'justify-end' : 'justify-start'} message-group message-enter`;
    }

    msgDiv.setAttribute('data-message-id', messageId);
    msgDiv.setAttribute('data-user-id', userId);
    if (userNewId) {
        msgDiv.setAttribute('data-user-new-id', userNewId);
    }

    const firstLetter = username.charAt(0).toUpperCase();
    const avatarImg = userAvatar ?
        `<img src="${userAvatar}" class="w-full h-full object-cover" loading="lazy">` :
        (isBot ? 'bot' : firstLetter);

    const avatarHTML = !isBot ?
        `<a href="/profile/${userId}" class="flex-shrink-0 w-8 h-8 rounded-full bg-indigo-600 flex items-center justify-center text-xs font-bold hover:ring-2 hover:ring-indigo-400 transition overflow-hidden sidebar-avatar">${avatarImg}</a>` :
        `<div class="bot-avatar-btn flex-shrink-0 w-8 h-8 rounded-full bg-gradient-to-br from-purple-500 to-pink-500 flex items-center justify-center text-lg shadow-lg cursor-pointer hover:scale-110 transition"
             data-bot-id="${botId || 0}"
             title="Открыть консоль бота"></div>`;

    let actionsHTML = '';
    if (isMine && !isBot) {
        actionsHTML = `
            <div class="message-actions absolute -top-3 -right-3 flex gap-1 bg-gray-800 rounded-lg p-1 shadow-lg">
                <button onclick="editMessage(${messageId})" class="p-1.5 bg-gray-600 hover:bg-blue-600 rounded text-white btn-edit" title="Редактировать">✏️</button>
                <button onclick="deleteMessage(${messageId})" class="p-1.5 bg-gray-600 hover:bg-red-600 rounded text-white btn-delete" title="Удалить">🗑️</button>
            </div>`;
    }

    const bubbleClass = isBot ? 'message-bubble bot-message bg-purple-900/50 rounded-xl p-3 border border-purple-700/50' : (isMine ? 'bg-indigo-600' : 'bg-gray-700');

    let imageHTML = '';
    if (imageUrl) {
        imageHTML = `<img src="${imageUrl}" class="mt-2 max-w-[250px] rounded-lg cursor-pointer hover:opacity-90 transition" onclick="openImageModal('${imageUrl}')">`;
    }

    msgDiv.innerHTML = `
        <div class="flex items-end gap-2 max-w-[85%]">
            ${!isMine && !isBot ? avatarHTML : ''}
            <div class="flex flex-col ${isMine ? 'items-end' : (isBot ? 'items-center' : 'items-start')}">
                ${!isBot ? `<div class="text-xs text-gray-400 mb-1">${username}</div>` : ''}
                <div class="p-3 rounded-lg ${bubbleClass} relative shadow-md">
                    <p class="text-sm message-content">${content}</p>
                    ${imageHTML} <!-- ✅ Вставляем изображение -->
                    ${actionsHTML}
                </div>
                <span class="text-xs text-gray-500 mt-1 message-time">${time}</span>
            </div>
            ${isMine ? avatarHTML : ''}
        </div>
    `;

    container.appendChild(msgDiv);
    container.scrollTop = container.scrollHeight;
}

function openImageModal(src) {
    const modal = document.createElement('div');
    modal.className = 'fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center z-50 p-4';
    modal.onclick = () => modal.remove();
    const img = document.createElement('img');
    img.src = src;
    img.className = 'max-h-[90vh] max-w-[90vw] object-contain rounded-lg';
    img.onclick = (e) => e.stopPropagation();
    modal.appendChild(img);
    document.body.appendChild(modal);
}

document.addEventListener('click', function(e) {
    const btn = e.target.closest('.bot-avatar-btn');
    if (btn) {
        const botId = btn.getAttribute('data-bot-id');
        if (botId && botId !== '0') {
            window.location.href = `/bots/console/${botId}`;
        }
    }
});

document.addEventListener('click', function(e) {
    const btn = e.target.closest('.roulette-reroll-btn');
    if (!btn || !socket) return;

    e.preventDefault();
    const box = btn.closest('[id^="wheel-"]');
    if (!box) return;

    let extraData = {};
    if (box.dataset.type === 'standard') {
        const titleEl = box.querySelector('[style*="font-size:35px"]');
        if (titleEl) extraData.title = titleEl.textContent.trim();

        const accentMatch = box.style.getPropertyValue('--accent');
        if (accentMatch) extraData.accent = accentMatch.trim();
    }

    socket.emit('roulette_reroll', {
        spin_id: box.id.replace('wheel-', ''),
        options: JSON.parse(box.dataset.options),
        winner: box.dataset.winner,
        type: box.dataset.type,
        ...extraData
    });
});

socket.on('roulette_updated', function(data) {
    const el = document.getElementById('wheel-' + data.spin_id);
    if (el) {
        const parent = el.parentElement;
        const originalWidth = parent ? parent.offsetWidth : el.offsetWidth;

        el.style.opacity = '0';
        setTimeout(() => {
            el.outerHTML = data.html;
            const newEl = document.getElementById('wheel-' + data.spin_id);
            if(newEl) {
                newEl.style.opacity = '1';
                newEl.style.maxWidth = '420px';
                newEl.style.width = '100%';
            }
        }, 300);
    }
});

setTimeout(() => {
    document.querySelectorAll('.roulette-reroll-btn').forEach(btn => {
        btn.style.display = 'block';
    });
}, 4200);