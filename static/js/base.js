function toggleMobileMenu() {
    const menu = document.getElementById('mobile-menu');
    const btn = document.getElementById('mobile-menu-btn');

    if (menu && btn) {
        const isOpen = menu.classList.toggle('hidden');
        btn.setAttribute('aria-expanded', !isOpen);
    }
}

function toggleUserMenu() {
    const menu = document.getElementById('user-menu');
    const btn = document.getElementById('user-menu-button');

    if (menu && btn) {
        const isOpen = menu.classList.toggle('hidden');
        btn.setAttribute('aria-expanded', !isOpen);
    }
}

document.addEventListener('click', function(e) {
    const userMenu = document.getElementById('user-menu');
    const userBtn = document.getElementById('user-menu-button');

    if (userMenu && !userMenu.classList.contains('hidden')) {
        if (!userBtn.contains(e.target) && !userMenu.contains(e.target)) {
            userMenu.classList.add('hidden');
            userBtn.setAttribute('aria-expanded', 'false');
        }
    }

    const mobileMenu = document.getElementById('mobile-menu');
    if (mobileMenu && !mobileMenu.classList.contains('hidden')) {
        if (e.target.tagName === 'A' && e.target.href.includes(window.location.hostname)) {
            mobileMenu.classList.add('hidden');
        }
    }
});

document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape') {
        const menus = ['user-menu', 'mobile-menu'];
        menus.forEach(id => {
            const el = document.getElementById(id);
            if (el && !el.classList.contains('hidden')) {
                el.classList.add('hidden');
            }
        });
    }
});

let resizeTimer;
window.addEventListener('resize', function() {
    clearTimeout(resizeTimer);
    resizeTimer = setTimeout(function() {
        if (window.innerWidth >= 768) {
            const mobileMenu = document.getElementById('mobile-menu');
            if (mobileMenu) mobileMenu.classList.add('hidden');
        }
    }, 250);
});

document.addEventListener('DOMContentLoaded', function() {
    if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
        document.documentElement.classList.add('dark');
    }

    const firstInput = document.querySelector('form input:not([type="hidden"]):not([disabled])');
    if (firstInput && !document.activeElement) {
        setTimeout(() => firstInput.focus(), 100);
    }
});