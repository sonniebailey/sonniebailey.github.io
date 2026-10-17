// @ts-check

/**
 * Solidify the floating header once the visitor scrolls off the hero.
 *
 * The header sits transparent over the hero photograph. Past the hero it
 * would be over running text, where transparent is unreadable, so the
 * solid surface is switched on by class. The threshold is the hero's own
 * height rather than a fixed number, so it works on every page size.
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

    const hero = document.querySelector('.hero');

    /**
     * Point at which the header stops floating, in pixels of scroll.
     * @returns {number}
     */
    function threshold() {
        if (!(hero instanceof HTMLElement)) return 0;
        return Math.max(hero.offsetHeight - header.offsetHeight, 0);
    }

    /**
     * Sync the class to the current scroll position.
     * @returns {void}
     */
    function sync() {
        header.classList.toggle('is-scrolled', window.scrollY > threshold());
    }

    // A page with no hero (should one exist) is solid from the start.
    if (!hero) {
        header.classList.add('is-scrolled');
        return;
    }

    sync();
    window.addEventListener('scroll', sync, { passive: true });
    window.addEventListener('resize', sync);
});
