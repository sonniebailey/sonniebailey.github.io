// @ts-check

/*
 * FAQ expand/collapse-all control.
 *
 * The accordions themselves are native <details> elements produced by
 * build/faq_transform.py and need no JavaScript. This file only adds the
 * one control a long FAQ page benefits from: a button that opens or
 * closes every question at once, whose label reflects what it will do
 * next.
 *
 * The button ships hidden and is revealed here, so a visitor without
 * JavaScript never sees a control that would not work.
 *
 * Does nothing if there is no .faq-list or no .faq-toggle-all on the
 * page, so this file is safe to load site-wide.
 */

(function () {
    'use strict';

    /**
     * Sync the button label and aria-expanded to the current state of the
     * accordions. The button offers "Collapse all" only when every item is
     * already open; otherwise it offers "Expand all".
     *
     * Args:
     *   button - the toggle-all button
     *   items - the list of <details> elements it controls
     * Returns: nothing
     * @param {HTMLElement} button
     * @param {NodeListOf<HTMLDetailsElement>} items
     * @returns {void}
     */
    function syncLabel(button, items) {
        var allOpen = true;
        for (var i = 0; i < items.length; i++) {
            if (!items[i].open) {
                allOpen = false;
                break;
            }
        }
        button.textContent = allOpen ? 'Collapse all' : 'Expand all';
        button.setAttribute('aria-expanded', String(allOpen));
    }

    /**
     * Reveal the control and wire it to the accordions on the page.
     *
     * Args: none
     * Returns: nothing
     * @returns {void}
     */
    function init() {
        var list = document.querySelector('.faq-list');
        var button = document.querySelector('.faq-toggle-all');
        if (!list || !button) return;

        var items = list.querySelectorAll('details');
        if (!items.length) return;

        // Seat the control row directly above the list it operates on, so
        // any preamble (eg the About page's opening paragraphs) sits above
        // the button and is visibly outside its reach. The row only exists
        // for JavaScript visitors, so moving it here costs no-JS nothing.
        var controls = button.closest('.faq-controls');
        if (controls && list.parentNode) {
            list.parentNode.insertBefore(controls, list);
        }

        button.removeAttribute('hidden');
        button.setAttribute('aria-controls', 'faq-list');
        list.id = 'faq-list';
        syncLabel(/** @type {HTMLElement} */ (button), items);

        button.addEventListener('click', function () {
            // Decide once from the current state, then apply that same
            // action to every item -- reading each item's own state as we
            // go would toggle them into disagreement.
            var shouldOpen = button.getAttribute('aria-expanded') !== 'true';
            for (var i = 0; i < items.length; i++) {
                items[i].open = shouldOpen;
            }
            syncLabel(/** @type {HTMLElement} */ (button), items);
        });

        // A visitor opening or closing one question by hand can make the
        // button's offer stale; re-sync whenever any item changes.
        for (var j = 0; j < items.length; j++) {
            items[j].addEventListener('toggle', function () {
                syncLabel(/** @type {HTMLElement} */ (button), items);
            });
        }
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
