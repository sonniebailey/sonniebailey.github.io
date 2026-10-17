// @ts-check

/*
 * Open and close native <dialog> popups.
 *
 * A button with data-dialog-open="<id>" opens the dialog with that id as
 * a modal; any [data-dialog-close] inside a dialog closes it, as does a
 * click on the dimmed area outside it, or Escape.
 *
 * The dialog grows out of the button that opened it and shrinks back
 * into it on close. Timing comes from --duration-dialog and --ease-dialog
 * in css/variables.css. Visitors who ask for reduced motion get an
 * instant open and close.
 *
 * Opening buttons ship hidden and are revealed here, so a visitor without
 * JavaScript never sees a control that would not work.
 *
 * Does nothing if the page has no such buttons, so it is safe to load
 * site-wide.
 */

(function () {
    'use strict';

    const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)');

    /**
     * Read the dialog animation timing from the CSS tokens.
     *
     * Returns: duration in milliseconds and easing string
     */
    function timing() {
        const root = getComputedStyle(document.documentElement);
        const duration = parseFloat(root.getPropertyValue('--duration-dialog')) * 1000;
        const easing = root.getPropertyValue('--ease-dialog').trim();
        return { duration: duration, easing: easing };
    }

    /**
     * Build the transform that shrinks the dialog onto the button.
     *
     * Args:
     *   dialog - the open dialog, at its full size and position
     *   button - the button it grows out of
     * Returns: a CSS transform string
     * LLM Note: must be measured while the dialog is open and untransformed.
     */
    function collapsedTransform(dialog, button) {
        const from = button.getBoundingClientRect();
        const to = dialog.getBoundingClientRect();
        const dx = (from.left + from.width / 2) - (to.left + to.width / 2);
        const dy = (from.top + from.height / 2) - (to.top + to.height / 2);
        const scale = from.width / to.width;
        return 'translate(' + dx + 'px, ' + dy + 'px) scale(' + scale + ')';
    }

    /**
     * Animate the dialog and its backdrop between button and full size.
     *
     * Args:
     *   dialog - the open dialog
     *   button - the button it grows out of
     *   opening - true to grow out, false to shrink back
     * Returns: the dialog's Animation, so the caller can wait on it
     */
    function animate(dialog, button, opening) {
        const t = timing();
        const collapsed = { transform: collapsedTransform(dialog, button), opacity: 0 };
        const expanded = { transform: 'none', opacity: 1 };
        const frames = opening ? [collapsed, expanded] : [expanded, collapsed];
        const fade = opening ? [{ opacity: 0 }, { opacity: 1 }] : [{ opacity: 1 }, { opacity: 0 }];

        dialog.animate(fade, { duration: t.duration, easing: t.easing, pseudoElement: '::backdrop', fill: 'forwards' });
        return dialog.animate(frames, { duration: t.duration, easing: t.easing, fill: 'forwards' });
    }

    /**
     * Wire one opening button to its dialog and reveal the button.
     *
     * Args:
     *   button - element carrying data-dialog-open
     * Returns: nothing
     * LLM Note: a button whose dialog id is missing stays hidden.
     */
    function wire(button) {
        const dialog = document.getElementById(button.dataset.dialogOpen || '');
        if (!(dialog instanceof HTMLDialogElement)) return;

        let closing = false;

        function open() {
            dialog.showModal();
            if (!reducedMotion.matches) animate(dialog, button, true);
        }

        function close() {
            if (closing || !dialog.open) return;
            if (reducedMotion.matches) {
                dialog.close();
                return;
            }
            closing = true;
            animate(dialog, button, false).finished.then(function () {
                dialog.close();
                dialog.getAnimations({ subtree: true }).forEach(function (a) { a.cancel(); });
                closing = false;
            });
        }

        button.hidden = false;
        button.addEventListener('click', open);

        dialog.querySelectorAll('[data-dialog-close]').forEach(function (closer) {
            closer.addEventListener('click', close);
        });

        // A click landing on the dialog element itself, not its content,
        // is a click on the dimmed backdrop.
        dialog.addEventListener('click', function (event) {
            if (event.target === dialog) close();
        });

        // Escape: hold the browser's instant close so the animation runs.
        dialog.addEventListener('cancel', function (event) {
            event.preventDefault();
            close();
        });
    }

    document.addEventListener('DOMContentLoaded', function () {
        document.querySelectorAll('[data-dialog-open]').forEach(function (button) {
            if (button instanceof HTMLElement) wire(button);
        });
    });
})();
