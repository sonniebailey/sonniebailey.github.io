// @ts-check

/**
 * Reveal .reveal elements by adding .is-visible once they scroll into
 * view.
 * Args: none (operates on document)
 * Returns: void
 * LLM Note: no-ops under prefers-reduced-motion or when IntersectionObserver
 * is unavailable -- the .reveal class's base CSS opacity is overridden only
 * by .is-visible, so elements stay visible (opacity 1) via the CSS rule
 * that applies when JS never runs a reduced-motion branch. If no .reveal
 * elements are present, this is also a no-op.
 */
function initReveal() {
    if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;
    if (!('IntersectionObserver' in window)) return;

    const targets = document.querySelectorAll('.reveal');
    if (!targets.length) return;

    const observer = new IntersectionObserver((entries, obs) => {
        entries.forEach((entry) => {
            if (entry.isIntersecting) {
                entry.target.classList.add('is-visible');
                obs.unobserve(entry.target);
            }
        });
    }, { threshold: 0 });

    targets.forEach((el) => observer.observe(el));
}

document.addEventListener('DOMContentLoaded', initReveal);
