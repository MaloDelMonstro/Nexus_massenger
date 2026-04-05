(function () {
    'use strict';

    const socket = window.socket;
    const currentUserId = window.currentUserId;
    const recipientId = window.recipientId;

    const messagesContainer = document.getElementById('messages-container');
    const messageForm = document.getElementById('message-form');
    const messageInput = document.getElementById('message-input');
    const toastContainer = document.getElementById('toast-container');


    window.editPrivateMessage = function (messageId, currentContent) {
        const newContent = prompt('Редактировать сообщение:', currentContent);
        if (newContent !== null && newContent.trim() !== '' && newContent !== currentContent) {
            fetch('/messages/' + messageId + '/edit', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                credentials: 'same-origin',
                body: JSON.stringify({content: newContent.trim()})
            })
                .then(function (r) {
                    return r.json();
                })
                .then(function (d) {
                    if (d.success) {
                        const msgEl = document.querySelector('[data-message-id="' + messageId + '"] .message-content');
                        if (msgEl) {
                            msgEl.innerHTML = escapeHtml(d.content) + ' <span class="text-xs text-gray-400">(изм.)</span>';
                        }
                        showToast('Сообщение изменено', 'success');
                    } else {
                        showToast('Ошибка: ' + d.error, 'error');
                    }
                })
                .catch(function () {
                    showToast('Ошибка сети', 'error');
                });
        }
    };

    window.deletePrivateMessage = function (messageId) {
        if (confirm('Удалить сообщение?')) {
            fetch('/messages/' + messageId + '/delete', {
                method: 'POST',
                credentials: 'same-origin'
            })
                .then(function (r) {
                    return r.json();
                })
                .then(function (d) {
                    if (d.success) {
                        const el = document.querySelector('[data-message-id="' + messageId + '"]');
                        if (el) {
                            el.classList.add('message-deleting');
                            setTimeout(function () {
                                el.remove();
                            }, 300);
                        }
                        showToast('Сообщение удалено', 'success');
                    } else {
                        showToast('Ошибка: ' + d.error, 'error');
                    }
                })
                .catch(function () {
                    showToast('Ошибка сети', 'error');
                });
        }
    };


    socket.on('connect', function () {
        socket.emit('join_private_room', {user_id: currentUserId});
        console.log('✅ Подключено к личным сообщениям');
    });

    socket.on('private_message', function (data) {
        if (data.sender_id === recipientId) {
            addMessage(data.content, data.timestamp, data.sender_id, data.id, data.sender_avatar);
            if (messagesContainer) {
                messagesContainer.scrollTop = messagesContainer.scrollHeight;
            }
        }
    });

    socket.on('private_message_sent', function (data) {
        if (data.recipient_id === recipientId) {
            addMessage(data.content, data.timestamp, data.sender_id, data.id, data.sender_avatar);
            if (messagesContainer) {
                messagesContainer.scrollTop = messagesContainer.scrollHeight;
            }
        }
    });

    socket.on('private_message_edited', function (data) {
        const msgEl = document.querySelector('[data-message-id="' + data.message_id + '"] .message-content');
        if (msgEl) {
            msgEl.innerHTML = escapeHtml(data.content) + ' <span class="text-xs text-gray-400">(изм.)</span>';
        }
        showToast('Сообщение изменено', 'info');
    });

    socket.on('private_message_deleted', function (data) {
        const el = document.querySelector('[data-message-id="' + data.message_id + '"]');
        if (el) {
            el.classList.add('message-deleting');
            setTimeout(function () {
                el.remove();
            }, 300);
        }
        showToast('Сообщение удалено', 'success');
    });

    if (messageForm && messageInput) {
        messageForm.addEventListener('submit', function (e) {
            e.preventDefault();
            const content = messageInput.value.trim();

            if (!content) {
                showToast('Введите сообщение', 'error');
                return;
            }

            if (!socket.connected) {
                showToast('Нет соединения с сервером', 'error');
                return;
            }

            socket.emit('send_private_message', {
                recipient_id: recipientId,
                content: content
            });

            messageInput.value = '';
            messageInput.focus();
        });

        messageInput.addEventListener('keydown', function (e) {
            if (e.key === 'Enter') {
                e.preventDefault();
                messageForm.requestSubmit();
            }
        });
    }

    function addMessage(content, time, senderId, messageId, senderAvatar) {
        const isMine = senderId === currentUserId;
        if (!messagesContainer) return;

        const msgDiv = document.createElement('div');
        msgDiv.className = 'flex ' + (isMine ? 'justify-end' : 'justify-start') + ' message-group message-enter';
        msgDiv.setAttribute('data-message-id', messageId);
        msgDiv.setAttribute('data-sender-id', senderId);

        const firstLetter = isMine ?
            (window.currentUsername || '?').charAt(0).toUpperCase() :
            (window.recipientUsername || '?').charAt(0).toUpperCase();

        const avatarImg = senderAvatar ?
            '<img src="' + escapeHtml(senderAvatar) + '" class="w-full h-full object-cover" loading="lazy">' :
            '<span class="avatar-initial" aria-hidden="true">' + firstLetter + '</span>';

        const profileUrl = isMine ? '/profile/' + currentUserId : '/profile/' + recipientId;
        const avatarHTML = '<a href="' + profileUrl + '" class="flex-shrink-0 w-8 h-8 rounded-full bg-indigo-600 flex items-center justify-center text-xs font-bold hover:ring-2 hover:ring-indigo-400 transition overflow-hidden" aria-label="Профиль">' + avatarImg + '</a>';

        let actionsHTML = '';
        if (isMine) {
            const escapedContent = JSON.stringify(content);
            actionsHTML = '<div class="message-actions absolute -top-3 -right-3 flex gap-1 bg-gray-800 rounded-lg p-1 shadow-lg opacity-0 group-hover:opacity-100 transition-opacity" role="group">' +
                '<button type="button" onclick="editPrivateMessage(' + messageId + ', ' + escapedContent + ')" class="p-1.5 bg-gray-600 hover:bg-blue-600 rounded text-white btn-edit-msg" aria-label="Редактировать">Изменить</button>' +
                '<button type="button" onclick="deletePrivateMessage(' + messageId + ')" class="p-1.5 bg-gray-600 hover:bg-red-600 rounded text-white btn-delete-msg" aria-label="Удалить">Удалить</button>' +
                '</div>';
        }

        msgDiv.innerHTML = '<div class="flex items-end gap-2 max-w-[85%]">' +
            (!isMine ? avatarHTML : '') +
            '<div class="flex flex-col ' + (isMine ? 'items-end' : 'items-start') + '">' +
            '<div class="p-3 rounded-lg ' + (isMine ? 'bg-indigo-600' : 'bg-gray-700') + ' relative shadow-md group message-bubble">' +
            '<p class="text-sm message-content break-words">' + escapeHtml(content) + '</p>' +
            actionsHTML +
            '</div>' +
            '<time class="text-xs text-gray-500 mt-1 message-time" datetime="' + new Date().toISOString() + '">' + escapeHtml(time) + '</time>' +
            '</div>' +
            (isMine ? avatarHTML : '') +
            '</div>';

        messagesContainer.appendChild(msgDiv);
    }

    function escapeHtml(text) {
        if (!text) return '';
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML.replace(/\n/g, '<br>');
    }

    function showToast(message, type) {
        if (!toastContainer) return;
        type = type || 'info';

        const toast = document.createElement('div');
        toast.className = 'px-4 py-2 rounded-lg shadow-lg text-sm font-medium pointer-events-auto ' +
            (type === 'success' ? 'bg-green-600 text-white' :
                type === 'error' ? 'bg-red-600 text-white' :
                    'bg-gray-700 text-white');
        toast.textContent = message;
        toast.setAttribute('role', 'alert');

        toastContainer.appendChild(toast);

        setTimeout(function () {
            toast.classList.add('toast-exit');
            setTimeout(function () {
                if (toast.parentNode) toast.parentNode.removeChild(toast);
            }, 300);
        }, 3000);
    }

    document.addEventListener('DOMContentLoaded', function () {
        if (messagesContainer) {
            messagesContainer.scrollTop = messagesContainer.scrollHeight;
        }
    });

})();