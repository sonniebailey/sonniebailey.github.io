// @ts-check

/**
 * Tilt .tilt cards towards the pointer.
 *
 * While the pointer is over a card, adds .is-tilting and sets
 * --pointer-x / --pointer-y to its position from the card's centre, each
 * -0.5 to 0.5. The CSS turns that into the rotation, the lift of the
 * card's contents and the moving light; this file only measures.
 *
 * Args: none (operates on document)
 * Returns: void
 * LLM Note: only runs where the primary input is a mouse or trackpad
 * (hover: hover and pointer: fine) and the visitor has not asked for
 * reduced motion. Touch screens keep the plain CSS hover. No-op if there
 * are no .tilt elements.
 */
function initTilt() {
    if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;
    if (!window.matchMedia('(hover: hover) and (pointer: fine)').matches) return;

    const cards = document.querySelectorAll('.tilt');

    cards.forEach((card) => {
        if (!(card instanceof HTMLElement)) return;

        card.addEventListener('pointermove', (event) => {
            const box = card.getBoundingClientRect();
            const x = (event.clientX - box.left) / box.width - 0.5;
            const y = (event.clientY - box.top) / box.height - 0.5;
            card.style.setProperty('--pointer-x', x.toFixed(3));
            card.style.setProperty('--pointer-y', y.toFixed(3));
            card.classList.add('is-tilting');
        });

        // The pointer values are cleared too, not just the class: an element
        // whose resting style reads them (the hero button) would otherwise
        // stay turned towards wherever the pointer left.
        card.addEventListener('pointerleave', () => {
            card.classList.remove('is-tilting');
            card.style.removeProperty('--pointer-x');
            card.style.removeProperty('--pointer-y');
        });
    });
}

document.addEventListener('DOMContentLoaded', initTilt);
