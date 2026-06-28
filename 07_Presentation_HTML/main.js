(function() {
    'use strict';

    // 1. إضافة ستايل العناصر اللي هتظهر خطوة بخطوة تلقائياً
    const style = document.createElement('style');
    style.innerHTML = `
        .step-item {
            opacity: 0;
            transform: translateY(15px);
            transition: opacity 0.4s ease-out, transform 0.4s ease-out;
            pointer-events: none;
        }
        .step-item.show {
            opacity: 1;
            transform: translateY(0);
            pointer-events: auto;
        }
    `;
    document.head.appendChild(style);

    // 2. دالة إظهار العنصر التالي
    function showNextStep() {
        const activeSlide = document.querySelector('.slide.on');
        if (!activeSlide) return false;

        const hiddenElements = activeSlide.querySelectorAll('.step-item:not(.show)');
        if (hiddenElements.length > 0) {
            hiddenElements[0].classList.add('show');
            return true; // أظهرنا عنصر، فامنع السلايد إنها تقلب
        }
        return false; // مفيش عناصر تانية، خلي السلايد تقلب عادي
    }

    // 3. التحكم في الكيبورد (الأسهم، المسطرة، PageDown)
    document.addEventListener('keydown', function(e) {
        if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') return;

        const forwardKeys = ['ArrowRight', 'ArrowDown', ' ', 'PageDown'];
        if (forwardKeys.includes(e.key)) {
            const activeSlide = document.querySelector('.slide.on');
            if (activeSlide && activeSlide.querySelectorAll('.step-item:not(.show)').length > 0) {
                e.preventDefault();
                e.stopImmediatePropagation(); // يمنع الكود الأساسي إنه يقلب السلايد
                showNextStep();
            }
        }
    }, true); 

    // 4. التحكم في الماوس (الضغط على زرار Next أو السلايد نفسها)
    document.addEventListener('click', function(e) {
        // استثناء الأزرار اللي مش المفروض تقلب السلايد خطوة بخطوة
        if (e.target.closest('#navPrev') || e.target.closest('.dots') ||
            e.target.closest('.fs-btn') || e.target.closest('a')) {
            return;
        }

        if (e.target.closest('#navNext') || e.target.closest('#deck')) {
            const activeSlide = document.querySelector('.slide.on');
            if (activeSlide && activeSlide.querySelectorAll('.step-item:not(.show)').length > 0) {
                e.preventDefault();
                e.stopImmediatePropagation();
                showNextStep();
            }
        }
    }, true);

    // 5. التحكم في اللمس (Swipe للموبايل والتابلت)
    let touchStartX = null;
    document.addEventListener('touchstart', e => { 
        touchStartX = e.changedTouches[0].clientX; 
    }, { passive: true, capture: true });
    
    document.addEventListener('touchend', e => {
        if (touchStartX === null) return;
        const dx = e.changedTouches[0].clientX - touchStartX;
        
        // لو سحب للشمال (يعني عايز يروح للسلايد اللي بعدها)
        if (dx < -50) {
            const activeSlide = document.querySelector('.slide.on');
            if (activeSlide && activeSlide.querySelectorAll('.step-item:not(.show)').length > 0) {
                e.stopImmediatePropagation();
                showNextStep();
            }
        }
        touchStartX = null;
    }, true);

    // 6. تتبع حركة السلايدز لترسيت العناصر (عشان تظهر من الأول لو رجعنا للسلايد)
    let lastSlideIndex = 0;
    const observer = new MutationObserver(function(mutations) {
        mutations.forEach(function(mutation) {
            if (mutation.attributeName === 'class') {
                const target = mutation.target;
                if (target.classList.contains('on')) {
                    const slides = Array.from(document.querySelectorAll('.slide'));
                    const newIdx = slides.indexOf(target);

                    if (newIdx !== -1) {
                        if (newIdx > lastSlideIndex) {
                            // لو بيتحرك لقدام: اخفي العناصر عشان تظهر واحدة واحدة
                            target.querySelectorAll('.step-item').forEach(el => el.classList.remove('show'));
                        } else if (newIdx < lastSlideIndex) {
                            // لو رجع لورا: اظهر كل العناصر فوراً عشان ميضطرش يضغط كتير وهو راجع
                            target.querySelectorAll('.step-item').forEach(el => el.classList.add('show'));
                        }
                        lastSlideIndex = newIdx;
                    }
                }
            }
        });
    });

    // تشغيل المراقبة أول ما الصفحة تحمل
    window.addEventListener('DOMContentLoaded', () => {
        // إضافة الكلاس step-item لكل العناصر المطلوبة عدا العناوين
        const elementsToAnimate = document.querySelectorAll(`
            .slide .pcard,
            .slide .stat-box,
            .slide .arch-layer,
            .slide .pipe-step,
            .slide .q-insight,
            .slide .formula,
            .slide .q-kpi,
            .slide .iframe-wrap,
            .slide .open-btn,
            .slide .tm,
            .slide .impact-card,
            .slide > .sc > p:not(.ss)
        `);
        
        elementsToAnimate.forEach(el => {
            el.classList.add('step-item');
        });

        document.querySelectorAll('.slide').forEach(slide => {
            observer.observe(slide, { attributes: true, attributeFilter: ['class'] });
        });
        
        // إخفاء العناصر في أول سلايد
        setTimeout(() => {
            const firstSlide = document.querySelector('.slide.on');
            if (firstSlide) {
                firstSlide.querySelectorAll('.step-item').forEach(el => el.classList.remove('show'));
            }
        }, 100);
    });

})();