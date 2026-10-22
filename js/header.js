// @ts-check

/**
 * Solidify the floating header once the visitor scrolls.
 *
 * At the top of the page the header is a light frost over the page
 * photograph. Once the page scrolls it would be over running text, where
 * that is hard to read, so the solid surface is switched on by class.
 *
 * Does nothing if there is no header, matching the other scripts here: a
 * template that drops the markup needs no JS change.
 *
 * Args: none (reads the DOM and the window scroll position)
 * Returns: void
 */
document.addEventListener('DOMContentLoaded', function () {
    const header = document.querySelector('header');
    if (!header) return;

    /**
     * Sync the class to the current scroll position.
     * @returns {void}
     */
    function sync() {
        header.classList.toggle('is-scrolled', window.scrollY > 0);
    }

    sync();
    window.addEventListener('scroll', sync, { passive: true });
});
