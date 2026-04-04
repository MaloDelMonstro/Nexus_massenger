document.addEventListener('DOMContentLoaded', function() {
    const searchInput = document.getElementById('user-search');
    const filterSelect = document.getElementById('filter-status');
    const sortSelect = document.getElementById('sort-by');
    const usersList = document.querySelector('.users-list');
    const usersCount = document.getElementById('users-count');
    const userCards = document.querySelectorAll('.user-card');

    function filterUsers() {
        const searchTerm = searchInput?.value?.toLowerCase() || '';
        const filterValue = filterSelect?.value || 'all';
        let visibleCount = 0;

        userCards.forEach(function(card) {
            if (card.classList.contains('empty-state')) return;

            const username = card.dataset.username || '';
            const email = card.dataset.email || '';
            const isAdmin = card.dataset.isAdmin === 'true';
            const isBanned = card.dataset.isBanned === 'true';
            const isVerified = card.dataset.isVerified === 'true';

            const matchesSearch = !searchTerm ||
                                  username.includes(searchTerm) ||
                                  email.includes(searchTerm);

            let matchesFilter = true;
            switch (filterValue) {
                case 'admin':
                    matchesFilter = isAdmin;
                    break;
                case 'verified':
                    matchesFilter = isVerified && !isBanned;
                    break;
                case 'banned':
                    matchesFilter = isBanned;
                    break;
                case 'unverified':
                    matchesFilter = !isVerified && !isBanned;
                    break;
            }

            if (matchesSearch && matchesFilter) {
                card.classList.remove('hidden');
                visibleCount++;
            } else {
                card.classList.add('hidden');
            }
        });

        if (usersCount) {
            usersCount.textContent = visibleCount;
        }

        const emptyState = document.querySelector('.empty-state');
        if (emptyState) {
            if (visibleCount === 0 && userCards.length > 0) {
                emptyState.style.display = 'block';
            } else {
                emptyState.style.display = 'none';
            }
        }
    }

    function sortUsers() {
        const sortBy = sortSelect?.value || 'created_desc';
        if (!usersList) return;

        const cards = Array.from(usersList.querySelectorAll('.user-card:not(.empty-state)'));

        cards.sort(function(a, b) {
            switch (sortBy) {
                case 'created_asc':
                    return new Date(a.dataset.created) - new Date(b.dataset.created);
                case 'name_asc':
                    return (a.dataset.username || '').localeCompare(b.dataset.username || '');
                case 'name_desc':
                    return (b.dataset.username || '').localeCompare(a.dataset.username || '');
                case 'created_desc':
                default:
                    return new Date(b.dataset.created) - new Date(a.dataset.created);
            }
        });

        cards.forEach(function(card) {
            usersList.appendChild(card);
        });
    }

    if (searchInput) {
        searchInput.addEventListener('input', filterUsers);
    }

    if (filterSelect) {
        filterSelect.addEventListener('change', filterUsers);
    }

    if (sortSelect) {
        sortSelect.addEventListener('change', sortUsers);
    }

    userCards.forEach(function(card) {
        if (card.classList.contains('empty-state')) return;

        card.addEventListener('keydown', function(e) {
            if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                this.click();
            }
        });
    });

    if (searchInput && userCards.length > 0) {
        searchInput.addEventListener('focus', function() {
            userCards.forEach(function(card) {
                if (!card.classList.contains('hidden')) {
                    card.classList.add('highlight');
                }
            });
        });

        searchInput.addEventListener('blur', function() {
            userCards.forEach(function(card) {
                card.classList.remove('highlight');
            });
        });
    }

    filterUsers();
});