document.addEventListener("DOMContentLoaded", () => {
    const carousels = document.querySelectorAll("[data-product-carousel]");
    carousels.forEach((carousel) => {
        const track = carousel.querySelector("[data-product-track]");
        const left = carousel.querySelector('[data-scroll-edge="left"]');
        const right = carousel.querySelector('[data-scroll-edge="right"]');
        if (!track || !left || !right) return;
        let speed = 0;
        let rafId = null;
        const tick = () => {
            if (speed !== 0) {
                track.scrollLeft += speed;
                rafId = requestAnimationFrame(tick);
            } else {
                rafId = null;
            }
        };
        const setSpeed = (value) => {
            speed = value;
            if (rafId === null && speed !== 0) {
                rafId = requestAnimationFrame(tick);
            }
        };
        left.addEventListener("mouseenter", () => setSpeed(-12));
        right.addEventListener("mouseenter", () => setSpeed(12));
        left.addEventListener("mouseleave", () => setSpeed(0));
        right.addEventListener("mouseleave", () => setSpeed(0));
        carousel.addEventListener("mouseleave", () => setSpeed(0));
    });
});
