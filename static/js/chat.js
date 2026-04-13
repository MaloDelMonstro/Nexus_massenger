/* static/js/chat.js */
console.log("🚀 Chat JS loaded");

// ==================== ГЛОБАЛЬНЫЕ ПЕРЕМЕННЫЕ ====================
const socket = io();
let messagesContainer;
let messageInput;
let sendBtn;
let imageUpload;
let urlContainer;
let urlField;
let previewBox;
let previewImg;
let pendingImageUrl = null;
let CURRENT_USER_ID = 0;

// ==================== ИНИЦИАЛИЗАЦИЯ ПОСЛЕ ЗАГРУЗКИ DOM ====================
window.addEventListener('load', () => {
    console.log("📦 Инициализация чата...");

    // Получаем элементы
    messagesContainer = document.getElementById('messages-container');
    messageInput = document.getElementById('message-input');
    sendBtn = document.getElementById('send-btn');
    imageUpload = document.getElementById('image-upload');
    urlContainer = document.getElementById('url-input-container');
    urlField = document.getElementById('image-url-field');
    previewBox = document.getElementById('image-preview-box');
    previewImg = document.getElementById('preview-img');

    // Получаем ID пользователя
    const bodyId = document.body.dataset.userId;
    if (bodyId) {
        CURRENT_USER_ID = parseInt(bodyId);
    }
    if (typeof window.currentUserId !== 'undefined') {
        CURRENT_USER_ID = window.currentUserId;
    }
    console.log("✅ Current User ID:", CURRENT_USER_ID);

    // 🔥 ВОССТАНАВЛИВАЕМ КАРТИНКУ ИЗ LOCALSTORAGE
    const savedImage = localStorage.getItem('pendingImageUrl');
    if (savedImage && previewImg && previewBox) {
        console.log("🔄 Восстановлена картинка:", savedImage);
        pendingImageUrl = savedImage;
        previewImg.src = savedImage;
        previewBox.classList.remove('hidden');
        if (urlContainer) urlContainer.classList.add('hidden');
    }

    // Скролл вниз
    if (messagesContainer) {
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }

    console.log("✅ Чат инициализирован");
});

// ==================== ОТПРАВКА ====================
window.sendMessage = function() {
    const text = messageInput ? messageInput.value.trim() : '';
    if (!text && !pendingImageUrl) return;

    console.log("📤 Отправка:", { text, image: pendingImageUrl });

    if (messageInput) messageInput.disabled = true;
    if (sendBtn) sendBtn.disabled = true;

    socket.emit('send_message', { message: text, image_url: pendingImageUrl });

    if (messageInput) messageInput.value = '';
    clearImageSelection();

    if (messageInput) messageInput.disabled = false;
    if (sendBtn) sendBtn.disabled = false;
    if (messageInput) messageInput.focus();
};

if (messageInput) {
    messageInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            window.sendMessage();
        }
    });
}

// ==================== ЗАГРУЗКА ФОТО ====================
window.handleFileSelect = function(input) {
    const file = input.files[0];
    if (!file) return;
    if (!file.type.startsWith('image/')) { alert('❌ Только изображения!'); input.value = ''; return; }

    const reader = new FileReader();
    reader.onload = (e) => {
        if (previewImg) previewImg.src = e.target.result;
        if (previewBox) previewBox.classList.remove('hidden');
        if (urlContainer) urlContainer.classList.add('hidden');
    };
    reader.readAsDataURL(file);

    const formData = new FormData();
    formData.append('image', file);

    fetch('/chat/upload-image', { method: 'POST', body: formData })
        .then(res => res.json())
        .then(data => {
            if (data.url) {
                pendingImageUrl = data.url;
                localStorage.setItem('pendingImageUrl', data.url); // ✅ СОХРАНЯЕМ
                console.log("✅ Фото загружено:", pendingImageUrl);
            } else {
                alert('Ошибка: ' + (data.error || 'Unknown'));
                clearImageSelection();
            }
        })
        .catch(err => { console.error("❌ Ошибка:", err); alert('Ошибка сети'); clearImageSelection(); });
};

// ==================== URL ====================
window.toggleUrlInput = function() {
    if (urlContainer) {
        urlContainer.classList.toggle('hidden');
        if (!urlContainer.classList.contains('hidden')) {
            if (urlField) urlField.focus();
            clearImageSelection();
        }
    }
};

if (urlField) {
    urlField.addEventListener('input', () => {
        const url = urlField.value.trim();
        if (url.startsWith('http')) {
            pendingImageUrl = url;
            localStorage.setItem('pendingImageUrl', url); // ✅ СОХРАНЯЕМ
            if (previewImg) previewImg.src = url;
            if (previewBox) previewBox.classList.remove('hidden');
            if (urlContainer) urlContainer.classList.add('hidden');
        }
    });
}

window.clearImageSelection = function() {
    pendingImageUrl = null;
    localStorage.removeItem('pendingImageUrl'); // ✅ ОЧИЩАЕМ
    if (imageUpload) imageUpload.value = '';
    if (urlField) urlField.value = '';
    if (urlContainer) urlContainer.classList.add('hidden');
    if (previewBox) previewBox.classList.add('hidden');
    if (previewImg) previewImg.src = '';
};

// ==================== SOCKET ====================
socket.on('connect', () => console.log("✅ Socket connected"));
socket.on('disconnect', () => console.log("❌ Socket disconnected"));

socket.on('new_message', (data) => {
    console.log("📨 Сообщение:", data);
    appendMessageToDOM(data);
    if (messagesContainer) messagesContainer.scrollTop = messagesContainer.scrollHeight;
});

socket.on('edit_allowed', (data) => {
    const newContent = prompt('✏️ Редактировать:', data.content);
    if (newContent !== null && newContent.trim() && newContent !== data.content) {
        fetch(`/chat/message/${data.message_id}/edit`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ content: newContent.trim() })
        }).then(res => res.json()).then(r => { if (!r.success) alert(r.error); })
          .catch(() => alert('Ошибка сети'));
    }
});

socket.on('delete_allowed', (data) => {
    if (confirm('🗑️ Удалить сообщение?')) {
        fetch(`/chat/message/${data.message_id}/delete`, { method: 'POST' })
            .then(res => res.json()).then(r => { if (!r.success) alert(r.error); })
            .catch(() => alert('Ошибка сети'));
    }
});

socket.on('message_edited', (data) => {
    const el = document.querySelector(`[data-message-id="${data.message_id}"] .message-content`);
    if (el) el.innerHTML = escapeHtml(data.content).replace(/\n/g, '<br>');
});

socket.on('message_deleted', (data) => {
    const el = document.querySelector(`[data-message-id="${data.message_id}"]`);
    if (el) { el.style.opacity = '0'; setTimeout(() => el.remove(), 300); }
});

socket.on('error', (data) => { console.error("❌ Ошибка:", data); alert(data.message || 'Ошибка'); });

// ==================== ОТОБРАЖЕНИЕ ====================
function appendMessageToDOM(data) {
    if (!messagesContainer) return;

    const msgUserId = parseInt(data.user_id);
    const isBot = data.is_bot || data.user_new_id === 'BOT' || msgUserId === 0;
    const isOwn = !isBot && CURRENT_USER_ID > 0 && msgUserId === CURRENT_USER_ID;

    console.log("  - Мой ID:", CURRENT_USER_ID, "| Отправитель:", msgUserId, "| Бот?", isBot, "| Своё?", isOwn);

    const msgDiv = document.createElement('div');
    msgDiv.className = `flex ${isOwn ? 'justify-end' : 'justify-start'} mb-4 message-group`;
    msgDiv.dataset.messageId = data.id;

    let imgHtml = '';
    if (data.image_url) {
        imgHtml = `<img src="${data.image_url}" class="mt-2 max-w-[250px] rounded-lg cursor-pointer hover:opacity-90 transition" onclick="openImageModal('${data.image_url}')">`;
    }

    let actionButtons = '';
    if (isOwn) {
        actionButtons = `
            <div class="message-actions absolute -top-3 -right-3 flex gap-1 bg-gray-800 rounded-lg p-1 shadow-lg">
                <button type="button" onclick="requestEditMessage(${data.id})" class="p-1.5 bg-gray-600 hover:bg-blue-600 rounded text-white" title="Редактировать">✏️</button>
                <button type="button" onclick="requestDeleteMessage(${data.id})" class="p-1.5 bg-gray-600 hover:bg-red-600 rounded text-white" title="Удалить">🗑️</button>
            </div>`;
    }

    // Аватарка
    let avatarHtml = '';
    if (!isOwn) {
        if (isBot) {
            avatarHtml = `
                <div class="flex-shrink-0 w-8 h-8 rounded-full bg-gradient-to-br from-purple-500 to-pink-500 flex items-center justify-center text-lg shadow-lg flex items-center justify-center">
                    🤖
                </div>`;
        } else {
            avatarHtml = `
                <a href="/profile/${data.user_id}" class="flex-shrink-0 w-8 h-8 rounded-full bg-indigo-600 flex items-center justify-center text-xs font-bold overflow-hidden">
                    ${data.user_avatar ? `<img src="${data.user_avatar}" class="w-full h-full object-cover">` : (data.username?.[0] || '?')}
                </a>`;
        }
    }

    let myAvatarHtml = '';
    if (isOwn) {
        myAvatarHtml = `
            <a href="/profile/${CURRENT_USER_ID}" class="flex-shrink-0 w-8 h-8 rounded-full bg-indigo-600 flex items-center justify-center text-xs font-bold overflow-hidden">
                ${data.user_avatar ? `<img src="${data.user_avatar}" class="w-full h-full object-cover">` : (data.username?.[0] || '?')}
            </a>`;
    }

    msgDiv.innerHTML = `
        <div class="flex items-end gap-2 max-w-[95%]">
            ${avatarHtml}
            <div class="flex flex-col ${isOwn ? 'items-end' : 'items-start'}">
                <div class="flex items-center gap-2 mb-1 ${isOwn ? 'flex-row-reverse' : ''}">
                    <span class="text-xs ${isBot ? 'text-purple-400' : 'text-gray-400'} font-medium">
                        ${data.username || (isBot ? '🤖 Nexus Bot' : 'User')}
                    </span>
                    <span class="text-xs text-gray-600">${data.time}</span>
                </div>
                <div class="p-3 rounded-lg ${isOwn ? 'bg-indigo-600' : (isBot ? 'bg-gray-800 border border-purple-500/30' : 'bg-gray-700')} relative shadow-md min-w-[100px]">
                    <div class="text-sm message-content break-words">${isBot ? data.text : escapeHtml(data.text).replace(/\n/g, '<br>')}</div>
                    ${imgHtml}
                    ${actionButtons}
                </div>
            </div>
            ${myAvatarHtml}
        </div>`;

    messagesContainer.appendChild(msgDiv);

    // ✅ После вставки запускаем скрипты рулетки (если есть)
    if (isBot) {
        const wheelContainer = msgDiv.querySelector('[id^="wheel-"]');
        if (wheelContainer) {
            // Перезапуск анимации рулетки
            const rw = wheelContainer.querySelector('.rw');
            if (rw) {
                rw.style.animation = 'none';
                void rw.offsetWidth; // force reflow
                rw.style.animation = '';
            }
        }
    }
}

// ==================== ГЛОБАЛЬНЫЕ ФУНКЦИИ ====================
window.requestEditMessage = function(messageId) {
    console.log("✏️ Запрос редактирования:", messageId);
    socket.emit('request_edit', { message_id: messageId });
};

window.requestDeleteMessage = function(messageId) {
    console.log("🗑️ Запрос удаления:", messageId);
    socket.emit('request_delete', { message_id: messageId });
};

window.openImageModal = function(url) {
    const modal = document.createElement('div');
    modal.className = 'fixed inset-0 bg-black/90 z-50 flex items-center justify-center p-4 cursor-zoom-out';
    modal.innerHTML = `<img src="${url}" class="max-w-full max-h-[90vh] rounded-lg shadow-2xl">`;
    modal.onclick = () => modal.remove();
    document.body.appendChild(modal);
};

function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}