// @ts-check

/*
 * Light/dark theme toggle.
 *
 * The theme lives in a data-theme attribute on <html> and is persisted in
 * localStorage under 'site-theme'. The initial value is applied by the
 * inline preload script in templates/partials/theme-preload.html, which
 * runs before first paint to avoid a flash of the wrong theme; this file
 * only handles clicks on the toggle and keeps its aria-label accurate.
 *
 * The button holds two inline SVG icons (sun and moon). CSS in
 * components.css shows the right one for the current theme, so there is
 * no icon swapping to do here.
 *
 * Does nothing if no toggle is present, so removing the button from the
 * header partial needs no change to this file.
 */

(function () {
    'use strict';

    var STORAGE_KEY = 'site-theme';

    /**
     * Read the theme currently applied to the document.
     *
     * Args: none
     * Returns: 'light' or 'dark'
     * @returns {'light' | 'dark'}
     */
    function getCurrentTheme() {
        return document.documentElement.getAttribute('data-theme') === 'dark'
            ? 'dark'
            : 'light';
    }

    /**
     * Describe the action the button would perform, for screen readers.
     * The visible icon is handled by CSS.
     *
     * Args:
     *   currentTheme - the theme that is active now
     * Returns: nothing
     * @param {'light' | 'dark'} currentTheme
     * @returns {void}
     */
    function updateToggles(currentTheme) {
        var next = currentTheme === 'dark' ? 'light' : 'dark';
        var toggles = document.querySelectorAll('.theme-toggle');
        for (var i = 0; i < toggles.length; i++) {
            toggles[i].setAttribute('aria-label', 'Switch to ' + next + ' theme');
            toggles[i].setAttribute('aria-pressed', String(currentTheme === 'dark'));
        }
    }

    /**
     * Apply a theme to the document and remember the choice.
     *
     * Args:
     *   theme - 'light' or 'dark'
     * Returns: nothing
     * @param {'light' | 'dark'} theme
     * @returns {void}
     */
    function setTheme(theme) {
        document.documentElement.setAttribute('data-theme', theme);
        try {
            localStorage.setItem(STORAGE_KEY, theme);
        } catch (e) {
            // Private mode: the choice applies for this page only.
        }
        updateToggles(theme);
    }

    /**
     * Wire up every toggle on the page (header and mobile menu).
     *
     * Args: none
     * Returns: nothing
     * @returns {void}
     */
    function init() {
        var toggles = document.querySelectorAll('.theme-toggle');
        if (!toggles.length) return;

        updateToggles(getCurrentTheme());

        for (var i = 0; i < toggles.length; i++) {
            toggles[i].addEventListener('click', function (event) {
                event.preventDefault();
                setTheme(getCurrentTheme() === 'dark' ? 'light' : 'dark');
            });
        }
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
