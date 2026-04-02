const socket = io();
const recipientId = {{ recipient.id }};
const currentUserId = {{ current_user.id }};

window.showToast = function(message, type = 'info') {
    const toastContainer = document.getElementById('toast-container');
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
};

window.escapeHtml = function(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML.replace(/\n/g, '<br>');
};

window.editPrivateMessage = function(messageId, currentContent) {
    const newContent = prompt('Редактировать сообщение:', currentContent);
    if (newContent !== null && newContent.trim() !== '' && newContent !== currentContent) {
        fetch(`/messages/${messageId}/edit`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            credentials: 'same-origin',
            body: JSON.stringify({ content: newContent.trim() })
        })
        .then(r => r.json())
        .then(d => {
            if (d.success) {
                const msgEl = document.querySelector(`[data-message-id="${messageId}"] .message-content`);
                if (msgEl) {
                    msgEl.innerHTML = d.content.replace(/\n/g, '<br>') + ' <span class="text-xs text-gray-400">(изм.)</span>';
                }
                window.showToast('Сообщение изменено', 'success');
            } else {
                window.showToast('Ошибка: ' + d.error, 'error');
            }
        })
        .catch(() => window.showToast('Ошибка сети', 'error'));
    }
};

window.deletePrivateMessage = function(messageId) {
    if (confirm('Удалить сообщение?')) {
        fetch(`/messages/${messageId}/delete`, {
            method: 'POST',
            credentials: 'same-origin'
        })
        .then(r => r.json())
        .then(d => {
            if (d.success) {
                const el = document.querySelector(`[data-message-id="${messageId}"]`);
                if (el) {
                    el.classList.add('message-deleting');
                    setTimeout(() => el.remove(), 300);
                }
                window.showToast('Сообщение удалено', 'success');
            } else {
                window.showToast('Ошибка: ' + d.error, 'error');
            }
        })
        .catch(() => window.showToast('Ошибка сети', 'error'));
    }
};

function addMessage(content, time, senderId, messageId, senderAvatar) {
    const isMine = senderId === currentUserId;
    const container = document.getElementById('messages-container');
    const msgDiv = document.createElement('div');
    msgDiv.className = `flex ${isMine ? 'justify-end' : 'justify-start'} message-group message-enter`;
    msgDiv.setAttribute('data-message-id', messageId);

    const firstLetter = isMine ? '{{ current_user.username[0].upper() }}' : '{{ recipient.username[0].upper() }}';
    const avatarUrl = senderAvatar || null;
    const profileUrl = isMine ? '/profile/{{ current_user.id }}' : '/profile/{{ recipient.id }}';

    const avatarHTML = `
        <a href="${profileUrl}" class="flex-shrink-0 w-8 h-8 rounded-full bg-indigo-600 flex items-center justify-center text-xs font-bold hover:ring-2 hover:ring-indigo-400 transition overflow-hidden">
            ${avatarUrl ? `<img src="${avatarUrl}" class="w-full h-full object-cover">` : firstLetter}
        </a>
    `;

    let actionsHTML = '';
    if (isMine) {
        const escapedContent = content.replace(/'/g, "\\'");
        actionsHTML = `
            <div class="message-actions absolute -top-3 -right-3 flex gap-1 bg-gray-800 rounded-lg p-1 shadow-lg">
                <button onclick="editPrivateMessage(${messageId}, '${escapedContent}')" class="p-1.5 bg-gray-600 hover:bg-blue-600 rounded text-white btn-edit-msg">Изменить</button>
                <button onclick="deletePrivateMessage(${messageId})" class="p-1.5 bg-gray-600 hover:bg-red-600 rounded text-white btn-delete-msg">Удалить</button>
            </div>
        `;
    }

    msgDiv.innerHTML = `
        <div class="flex items-end gap-2 max-w-[85%]">
            ${!isMine ? avatarHTML : ''}
            <div class="flex flex-col ${isMine ? 'items-end' : 'items-start'}">
                <div class="p-3 rounded-lg ${isMine ? 'bg-indigo-600' : 'bg-gray-700'} relative shadow-md group">
                    <p class="text-sm message-content break-words">${escapeHtml(content)}</p>
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

socket.on('connect', function() {
    socket.emit('join_private_room', { user_id: currentUserId });
});

socket.on('private_message', function(data) {
    if (data.sender_id === recipientId) {
        addMessage(data.content, data.timestamp, data.sender_id, data.id, data.sender_avatar);
    }
});

socket.on('private_message_sent', function(data) {
    if (data.recipient_id === recipientId) {
        addMessage(data.content, data.timestamp, data.sender_id, data.id, data.sender_avatar);
    }
});

socket.on('private_message_edited', function(data) {
    const msgEl = document.querySelector(`[data-message-id="${data.message_id}"] .message-content`);
    if (msgEl) {
        msgEl.innerHTML = data.content.replace(/\n/g, '<br>') + ' <span class="text-xs text-gray-400">(изм.)</span>';
    }
    window.showToast('Сообщение изменено', 'info');
});

socket.on('private_message_deleted', function(data) {
    const el = document.querySelector(`[data-message-id="${data.message_id}"]`);
    if (el) {
        el.classList.add('message-deleting');
        setTimeout(() => el.remove(), 300);
    }
});

const MAX_LINE_LENGTH = 100;
const MAX_MESSAGE_LENGTH = 5000;

function autoWrapLines(textarea) {
    const text = textarea.value;
    const lines = text.split('\n');
    let modified = false;
    let newLines = [];

    for (let line of lines) {
        if (line.length <= MAX_LINE_LENGTH) {
            newLines.push(line);
            continue;
        }
        while (line.length > MAX_LINE_LENGTH) {
            let wrapIndex = line.lastIndexOf(' ', MAX_LINE_LENGTH);
            if (wrapIndex === -1 || wrapIndex === 0) {
                wrapIndex = MAX_LINE_LENGTH;
            }
            newLines.push(line.substring(0, wrapIndex).trim());
            line = line.substring(wrapIndex).trim();
            modified = true;
        }
        if (line) {
            newLines.push(line);
        }
    }

    if (modified) {
        textarea.value = newLines.join('\n');
    }
    return modified;
}

function validateMessage(text) {
    if (!text || !text.trim()) return { valid: false, error: "Пустое сообщение" };
    if (text.length > MAX_MESSAGE_LENGTH) {
        return { valid: false, error: `Сообщение слишком длинное (макс. ${MAX_MESSAGE_LENGTH} символов)` };
    }
    const lines = text.split('\n');
    for (let i = 0; i < lines.length; i++) {
        if (lines[i].length > MAX_LINE_LENGTH) {
            return { valid: false, error: `Строка ${i + 1} превышает лимит` };
        }
    }
    return { valid: true, error: null };
}

document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('message-form');
    const input = document.getElementById('message-input');
    const container = document.getElementById('messages-container');

    if (container) {
        container.scrollTop = container.scrollHeight;
    }

    if (input) {
        input.addEventListener('input', function() {
            autoWrapLines(this);
            const text = this.value;
            const lines = text.split('\n');
            const longestLine = Math.max(...lines.map(l => l.length), 0);
            if (longestLine > MAX_LINE_LENGTH || text.length > MAX_MESSAGE_LENGTH) {
                this.classList.add('border-red-500');
            } else {
                this.classList.remove('border-red-500');
            }
        });

        input.addEventListener('keydown', function(e) {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                if (form) {
                    form.dispatchEvent(new Event('submit'));
                }
            }
        });
    }

    if (form && input) {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            e.stopPropagation();

            const content = input.value.trim();
            const validation = validateMessage(content);

            if (!validation.valid) {
                window.showToast(validation.error, 'error');
                input.focus();
                return;
            }

            if (!content) return;

            if (!socket || !socket.connected) {
                window.showToast('Нет соединения с сервером', 'error');
                return;
            }

            socket.emit('send_private_message', {
                recipient_id: recipientId,
                content: content
            });

            input.value = '';
            input.focus();
        });
    }
});