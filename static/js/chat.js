// Основной скрипт чата
// window.currentUserId уже установлен в HTML шаблоне
// window.socket уже создан в HTML шаблоне

function toggleSidebar() {
    const sidebar = document.getElementById('sidebar');
    const overlay = document.getElementById('overlay');
    if (!sidebar || !overlay) return;

    const isOpen = sidebar.classList.toggle('open');
    overlay.classList.toggle('active');
    sidebar.style.setProperty('transform', isOpen ? 'translateX(0)' : 'translateX(-100%)', 'important');

    const mainContent = document.querySelector('.main-content');
    if (mainContent && window.innerWidth >= 768) {
        mainContent.style.setProperty('margin-left', isOpen ? '320px' : '0', 'important');
    }
}

window.showToast = function(message, type) {
    type = type || 'info';
    const container = document.getElementById('toast-container');
    if (!container) return;

    const toast = document.createElement('div');
    let toastClass = 'toast-enter px-4 py-2 rounded-lg shadow-lg text-sm font-medium pointer-events-auto ';
    if (type === 'success') {
        toastClass += 'bg-green-600 text-white';
    } else if (type === 'error') {
        toastClass += 'bg-red-600 text-white';
    } else {
        toastClass += 'bg-gray-700 text-white';
    }
    toast.className = toastClass;
    toast.textContent = message;
    container.appendChild(toast);

    setTimeout(function() {
        toast.classList.add('toast-exit');
        setTimeout(function() {
            if (toast.parentNode) {
                toast.parentNode.removeChild(toast);
            }
        }, 300);
    }, 3000);
};

window.editMessage = function(messageId) {
    if (window.socket && window.socket.connected) {
        window.socket.emit('request_edit', { message_id: messageId });
    } else {
        window.showToast('Нет соединения с сервером', 'error');
    }
};

window.deleteMessage = function(messageId) {
    if (confirm('Удалить сообщение?')) {
        if (window.socket && window.socket.connected) {
            window.socket.emit('request_delete', { message_id: messageId });
        } else {
            window.showToast('Нет соединения с сервером', 'error');
        }
    }
};

window.escapeHtml = function(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML.replace(/\n/g, '<br>');
};

function addMessageToDOM(content, username, time, messageId, userId, userNewId, userAvatar) {
    const isMine = userId === window.currentUserId;
    const container = document.getElementById('messages-container');
    if (!container) return;

    const msgDiv = document.createElement('div');
    msgDiv.className = 'flex ' + (isMine ? 'justify-end' : 'justify-start') + ' message-group message-enter';
    msgDiv.setAttribute('data-message-id', messageId);

    const firstLetter = username.charAt(0).toUpperCase();
    const profileUrl = '/profile/' + userId;
    const avatarImg = userAvatar ? '<img src="' + userAvatar + '" class="w-full h-full object-cover">' : firstLetter;
    const avatarHTML = '<a href="' + profileUrl + '" class="flex-shrink-0 w-8 h-8 rounded-full bg-indigo-600 flex items-center justify-center text-xs font-bold hover:ring-2 hover:ring-indigo-400 transition overflow-hidden sidebar-avatar">' + avatarImg + '</a>';

    const escapedContent = window.escapeHtml(content);

    let actionsHTML = '';
    if (isMine) {
        actionsHTML = '<div class="message-actions absolute -top-3 -right-3 flex gap-1 bg-gray-800 rounded-lg p-1 shadow-lg">' +
            '<button onclick="editMessage(' + messageId + ')" class="p-1.5 bg-gray-600 hover:bg-blue-600 rounded text-white btn-edit">Изменить</button>' +
            '<button onclick="deleteMessage(' + messageId + ')" class="p-1.5 bg-gray-600 hover:bg-red-600 rounded text-white btn-delete">Удалить</button>' +
            '</div>';
    }

    msgDiv.innerHTML = '<div class="flex items-end gap-2 max-w-[85%]">' +
        (!isMine ? avatarHTML : '') +
        '<div class="flex flex-col ' + (isMine ? 'items-end' : 'items-start') + '">' +
        '<div class="p-3 rounded-lg ' + (isMine ? 'bg-indigo-600' : 'bg-gray-700') + ' relative shadow-md">' +
        '<p class="text-sm message-content">' + escapedContent + '</p>' +
        actionsHTML +
        '</div>' +
        '<span class="text-xs text-gray-500 mt-1 message-time">' + time + '</span>' +
        '</div>' +
        (isMine ? avatarHTML : '') +
        '</div>';

    container.appendChild(msgDiv);
    container.scrollTop = container.scrollHeight;
}

document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('chat-form');
    const input = document.getElementById('message-input');
    const container = document.getElementById('messages-container');

    if (container) {
        container.scrollTop = container.scrollHeight;
    }

    if (form && input) {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            const message = input.value.trim();

            if (!message) {
                window.showToast('Введите сообщение', 'error');
                return;
            }

            if (!window.socket || !window.socket.connected) {
                window.showToast('Нет соединения с сервером', 'error');
                return;
            }

            window.socket.emit('send_message', { message: message });
            input.value = '';
            input.style.height = 'auto';
            input.focus();
        });

        input.addEventListener('keydown', function(e) {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                form.dispatchEvent(new Event('submit'));
            }
        });

        input.addEventListener('input', function() {
            this.style.height = 'auto';
            this.style.height = Math.min(this.scrollHeight, 150) + 'px';
        });
    }

    const searchInput = document.getElementById('chat-search');
    if (searchInput) {
        searchInput.addEventListener('input', function(e) {
            const query = e.target.value.toLowerCase();
            document.querySelectorAll('.chat-item').forEach(function(item) {
                const text = item.textContent.toLowerCase();
                item.style.display = text.includes(query) ? 'block' : 'none';
            });
        });
    }

    if (window.socket) {
        window.socket.on('connect', function() {
            window.showToast('Подключено', 'success');
        });

        window.socket.on('disconnect', function() {
            window.showToast('Потеря связи', 'error');
        });

        window.socket.on('new_message', function(data) {
            addMessageToDOM(data.text, data.username, data.time, data.id, data.user_id, data.user_new_id, data.user_avatar);
        });

        window.socket.on('message_edited', function(data) {
            const el = document.querySelector('[data-message-id="' + data.message_id + '"] .message-content');
            if (el) {
                el.innerHTML = window.escapeHtml(data.content) + ' <span class="text-xs text-gray-400">(изм.)</span>';
                window.showToast('Сообщение изменено', 'success');
            }
        });

        window.socket.on('message_deleted', function(data) {
            const el = document.querySelector('[data-message-id="' + data.message_id + '"]');
            if (el) {
                el.classList.add('message-deleting');
                setTimeout(function() {
                    el.remove();
                }, 300);
                window.showToast('Сообщение удалено', 'success');
            }
        });

        window.socket.on('edit_allowed', function(data) {
            const newText = prompt('Редактировать сообщение:', data.content);
            if (newText && newText.trim()) {
                fetch('/message/' + data.message_id + '/edit', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    credentials: 'same-origin',
                    body: JSON.stringify({ content: newText.trim() })
                })
                .then(function(r) { return r.json(); })
                .then(function(d) {
                    if (d.error) {
                        window.showToast('Ошибка: ' + d.error, 'error');
                    } else {
                        window.showToast('Изменено', 'success');
                    }
                })
                .catch(function(e) {
                    window.showToast('Ошибка: ' + e, 'error');
                });
            }
        });

        window.socket.on('delete_allowed', function(data) {
            fetch('/message/' + data.message_id + '/delete', {
                method: 'POST',
                credentials: 'same-origin'
            })
            .then(function(r) { return r.json(); })
            .then(function(d) {
                if (d.error) {
                    window.showToast('Ошибка: ' + d.error, 'error');
                } else {
                    window.showToast('Удалено', 'success');
                }
            })
            .catch(function(e) {
                window.showToast('Ошибка: ' + e, 'error');
            });
        });

        window.socket.on('error', function(data) {
            window.showToast('Ошибка: ' + data.message, 'error');
        });
    }
});