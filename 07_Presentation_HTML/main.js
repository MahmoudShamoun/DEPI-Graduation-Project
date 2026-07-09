function showNextStep() {
    const activeSlide = document.querySelector('.slide.on');
    const container = activeSlide || document;
    const hiddenElements = container.querySelectorAll('.step-item:not(.show)');
    if (hiddenElements.length > 0) {
        hiddenElements[0].classList.add('show');
        return true;
    }
    return false;
}

// Track current slide index for intelligent reset / auto-reveal on back navigation
(function() {
    const slides = Array.from(document.querySelectorAll('.slide'));
    let currentSlideIndex = slides.findIndex(slide => slide.classList.contains('on'));
    if (currentSlideIndex === -1) currentSlideIndex = 0;

    // Intercept click event in the capture phase
    document.addEventListener('click', function(e) {
        // If user clicked previous arrow, don't intercept (let them go back naturally)
        if (e.target.closest('#navPrev')) {
            return;
        }

        const activeSlide = document.querySelector('.slide.on');
        if (activeSlide) {
            const hiddenElements = activeSlide.querySelectorAll('.step-item:not(.show)');
            if (hiddenElements.length > 0) {
                e.preventDefault();
                e.stopPropagation();
                e.stopImmediatePropagation();
                showNextStep();
            }
        }
    }, true);

    // Intercept keydown event in the capture phase
    document.addEventListener('keydown', function(e) {
        if (e.key === ' ' || e.key === 'ArrowRight' || e.key === 'ArrowDown') {
            const activeSlide = document.querySelector('.slide.on');
            if (activeSlide) {
                const hiddenElements = activeSlide.querySelectorAll('.step-item:not(.show)');
                if (hiddenElements.length > 0) {
                    e.preventDefault();
                    e.stopPropagation();
                    e.stopImmediatePropagation();
                    showNextStep();
                }
            }
        }
    }, true);

    // Monitor slide transitions to handle step-item states dynamically
    const observer = new MutationObserver(function(mutations) {
        mutations.forEach(function(mutation) {
            if (mutation.type === 'attributes' && mutation.attributeName === 'class') {
                const target = mutation.target;
                if (target.classList.contains('on')) {
                    const newIdx = slides.indexOf(target);
                    if (newIdx !== -1) {
                        if (newIdx > currentSlideIndex) {
                            // Moving forward: reset step-items on the new slide to be hidden
                            target.querySelectorAll('.step-item').forEach(el => el.classList.remove('show'));
                        } else if (newIdx < currentSlideIndex) {
                            // Moving backward: show all step-items on the new slide immediately
                            target.querySelectorAll('.step-item').forEach(el => el.classList.add('show'));
                        }
                        currentSlideIndex = newIdx;
                    }
                }
            }
        });
    });

    slides.forEach(slide => {
        observer.observe(slide, { attributes: true, attributeFilter: ['class'] });
    });
})();
