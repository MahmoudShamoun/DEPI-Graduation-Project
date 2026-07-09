document.addEventListener("DOMContentLoaded", () => {
    const slides = document.querySelectorAll(".slide");
    const dotsContainer = document.getElementById("dots-container");
    const counter = document.getElementById("slide-counter");
    const leftArrow = document.querySelector(".left-arrow");
    const rightArrow = document.querySelector(".right-arrow");
    const fullscreenBtn = document.querySelector(".fullscreen-btn");

    let currentSlide = 0;

    // Generate dots dynamically based on slide count
    slides.forEach((_, index) => {
        const dot = document.createElement("div");
        dot.classList.add("dot");
        if (index === 0) dot.classList.add("active");
        
        // Click dot to navigate
        dot.addEventListener("click", () => goToSlide(index));
        dotsContainer.appendChild(dot);
    });

    const dots = document.querySelectorAll(".dot");

    // Update DOM to reflect current slide
    function updateUI() {
        slides.forEach((slide, index) => {
            if (index === currentSlide) {
                slide.classList.add("active");
            } else {
                slide.classList.remove("active");
            }
        });
        
        dots.forEach((dot, index) => {
            if (index === currentSlide) {
                dot.classList.add("active");
                // Scroll dot container if necessary to keep active dot visible
                dot.scrollIntoView({ behavior: 'smooth', block: 'nearest', inline: 'center' });
            } else {
                dot.classList.remove("active");
            }
        });

        counter.textContent = `${currentSlide + 1} / ${slides.length}`;
    }

    function nextSlide() {
        if (currentSlide < slides.length - 1) {
            currentSlide++;
            updateUI();
        }
    }

    function prevSlide() {
        if (currentSlide > 0) {
            currentSlide--;
            updateUI();
        }
    }

    function goToSlide(index) {
        currentSlide = index;
        updateUI();
    }

    // Click UI arrows
    rightArrow.addEventListener("click", nextSlide);
    leftArrow.addEventListener("click", prevSlide);

    // Keyboard navigation
    document.addEventListener("keydown", (e) => {
        // Next Slide Triggers
        if (["ArrowRight", "Space", "PageDown"].includes(e.code)) {
            if (e.code === "Space") e.preventDefault(); // Prevent page scrolling
            nextSlide();
        }
        // Previous Slide Triggers
        if (["ArrowLeft", "PageUp"].includes(e.code)) {
            prevSlide();
        }
    });

    // Fullscreen toggle logic
    fullscreenBtn.addEventListener("click", () => {
        if (!document.fullscreenElement) {
            document.documentElement.requestFullscreen().catch(err => {
                console.warn(`Error attempting to enable fullscreen: ${err.message}`);
            });
        } else {
            if (document.exitFullscreen) {
                document.exitFullscreen();
            }
        }
    });

    // Initialize UI state
    updateUI();
});
