// @ts-check

/**
 * Aim a ray of light from the hero's top right corner at the pointer, and
 * swell it as the pointer comes down to the hero button's level.
 *
 * While the pointer is over .hero, adds .is-lit to it and sets two custom
 * properties on its .hero__light layer: --ray-angle, the turn in degrees
 * clockwise from pointing straight down that points the ray from the
 * corner at the pointer, and --ray-boost, 0 to 1, how near the pointer
 * is to the button's level (1 anywhere level with or below its top
 * edge). Keyboard focus on the button lights the
 * ray too, aimed at the button at full boost. Both values ease after
 * their targets rather than jumping: each frame closes a fixed share of
 * the gap, and the frame loop stops once they have caught up, so nothing
 * runs while the pointer is still.
 *
 * Args: none (operates on document)
 * Returns: void
 * LLM Note: the CSS turns, widens and fades the ray by transform and
 * opacity only, which is what keeps this cheap; do not switch it to
 * changing the gradient itself, which repaints the whole hero each frame.
 * The corner is the rotation origin set in base.css
 * (.hero__light::before); change both together. Only runs with a mouse
 * or trackpad and without reduced motion; no-op if the hero or its light
 * layer is missing. A hero with no button never boosts.
 */
function initHeroLight() {
    if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;
    if (!window.matchMedia('(hover: hover) and (pointer: fine)').matches) return;

    const hero = document.querySelector('.hero');
    const light = hero && hero.querySelector('.hero__light');
    if (!(hero instanceof HTMLElement) || !(light instanceof HTMLElement)) return;

    const button = hero.querySelector('.hero__cta');

    // Share of the remaining gap covered each frame: higher follows more
    // tightly, lower trails further behind.
    const FOLLOW = 0.2;
    // How far above the button's top edge, in px, the ray starts to swell.
    const REACH = 420;
    // Close enough to stop the loop: px for the aim, a fraction for boost.
    const SETTLED = 0.5;
    const SETTLED_BOOST = 0.005;

    const target = { x: 0, y: 0, boost: 0 };
    const current = { x: 0, y: 0, boost: 0 };
    let width = 0;
    let pointerInside = false;
    let running = false;

    /**
     * How close a point in the hero is to the button's level, eased so the
     * swell gathers gently and then builds. Only height counts: anywhere
     * level with or below the button's top edge is full, whatever the
     * horizontal position, and above it the swell falls away over REACH.
     * @param {number} y - px from the hero's top
     * @param {DOMRect} heroBox
     * @returns {number} 0 (REACH or more above the button) to 1 (level with or below it)
     */
    function closeness(y, heroBox) {
        if (!(button instanceof HTMLElement)) return 0;
        const top = button.getBoundingClientRect().top - heroBox.top;
        const near = 1 - Math.min(Math.max(top - y, 0) / REACH, 1);
        return near * near * (3 - 2 * near);
    }

    /**
     * Set the targets from a point in viewport coordinates.
     * @param {number} clientX
     * @param {number} clientY
     * @returns {void}
     */
    function aimAt(clientX, clientY) {
        const box = hero.getBoundingClientRect();
        width = box.width;
        target.x = clientX - box.left;
        target.y = clientY - box.top;
        target.boost = closeness(target.y, box);
    }

    /**
     * Write the current aim and boost onto the layer.
     * @returns {void}
     */
    function write() {
        const dx = current.x - width;
        const angle = Math.atan2(-dx, current.y) * (180 / Math.PI);
        light.style.setProperty('--ray-angle', `${angle.toFixed(2)}deg`);
        light.style.setProperty('--ray-boost', current.boost.toFixed(3));
    }

    /**
     * Move one step towards the targets, and keep going until caught up.
     * @returns {void}
     */
    function step() {
        current.x += (target.x - current.x) * FOLLOW;
        current.y += (target.y - current.y) * FOLLOW;
        current.boost += (target.boost - current.boost) * FOLLOW;
        write();

        const settled = Math.abs(target.x - current.x) < SETTLED
            && Math.abs(target.y - current.y) < SETTLED
            && Math.abs(target.boost - current.boost) < SETTLED_BOOST;
        if (settled) {
            running = false;
            return;
        }
        window.requestAnimationFrame(step);
    }

    /**
     * Start the frame loop if it is not already running.
     * @returns {void}
     */
    function run() {
        if (running) return;
        running = true;
        window.requestAnimationFrame(step);
    }

    /**
     * Jump straight to the targets, for when the ray first appears.
     * @returns {void}
     */
    function snap() {
        current.x = target.x;
        current.y = target.y;
        current.boost = target.boost;
        write();
    }

    hero.addEventListener('pointerenter', (event) => {
        pointerInside = true;
        // Aim where the pointer came in, not where it last left.
        aimAt(event.clientX, event.clientY);
        if (!hero.classList.contains('is-lit')) snap();
        hero.classList.add('is-lit');
        run();
    });

    hero.addEventListener('pointermove', (event) => {
        aimAt(event.clientX, event.clientY);
        run();
    });

    hero.addEventListener('pointerleave', () => {
        pointerInside = false;
        if (button !== document.activeElement) hero.classList.remove('is-lit');
    });

    if (button instanceof HTMLElement) {
        button.addEventListener('focus', () => {
            const b = button.getBoundingClientRect();
            aimAt(b.left + b.width / 2, b.top + b.height / 2);
            if (!hero.classList.contains('is-lit')) snap();
            hero.classList.add('is-lit');
            run();
        });

        button.addEventListener('blur', () => {
            if (!pointerInside) hero.classList.remove('is-lit');
        });
    }
}

document.addEventListener('DOMContentLoaded', initHeroLight);
