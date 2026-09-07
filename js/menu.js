// @ts-check

/**
 * Mobile burger menu: opens #mobile-menu, closes on the close button,
 * Escape, or a nav-link click, and returns focus to the toggle button
 * on close.
 * Args: none (operates on document)
 * Returns: void
 * LLM Note: no-ops entirely if button.menu-toggle or nav#mobile-menu is
 * absent from the page, per the contract's markup hooks.
 */
function initMenu() {
    const toggle = /** @type {HTMLButtonElement | null} */ (document.querySelector('button.menu-toggle'));
    const menu = document.getElementById('mobile-menu');
    if (!toggle || !menu) return;

    const closeBtn = menu.querySelector('.menu-close');
    const links = menu.querySelectorAll('a');

    const openMenu = () => {
        menu.hidden = false;
        toggle.setAttribute('aria-expanded', 'true');
        document.body.style.overflow = 'hidden';
    };

    const closeMenu = () => {
        menu.hidden = true;
        toggle.setAttribute('aria-expanded', 'false');
        document.body.style.overflow = '';
        toggle.focus();
    };

    toggle.addEventListener('click', () => {
        const isOpen = toggle.getAttribute('aria-expanded') === 'true';
        if (isOpen) {
            closeMenu();
        } else {
            openMenu();
        }
    });

    if (closeBtn) {
        closeBtn.addEventListener('click', closeMenu);
    }

    links.forEach((link) => {
        link.addEventListener('click', closeMenu);
    });

    document.addEventListener('keydown', (event) => {
        if (event.key === 'Escape' && !menu.hidden) {
            closeMenu();
        }
    });
}

document.addEventListener('DOMContentLoaded', initMenu);
