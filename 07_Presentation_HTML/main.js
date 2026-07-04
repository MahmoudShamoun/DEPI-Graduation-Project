/**
 * Step-by-step reveal controller for the presentation deck.
 *
 * Elements marked with the `.step-item` class inside the active slide are
 * revealed one at a time (via keyboard, click, or swipe) before the deck is
 * allowed to advance to the next slide. Navigating backward reveals all
 * step-items on the target slide immediately, so the presenter never has to
 * re-click through content they've already shown.
 */
(function () {
  'use strict';

  // ── Selectors for elements that should be revealed step-by-step. ──
  // (Slide titles/subtitles are intentionally excluded — they animate in
  // immediately via CSS when a slide becomes active.)
  const STEP_ITEM_SELECTOR = [
    '.slide .pcard',
    '.slide .stat-box',
    '.slide .arch-layer',
    '.slide .pipe-step',
    '.slide .q-insight',
    '.slide .formula',
    '.slide .q-kpi',
    '.slide .iframe-wrap',
    '.slide .open-btn',
    '.slide .tm',
    '.slide .impact-card',
    '.slide > .sc > p:not(.ss)',
  ].join(',\n');

  const SWIPE_THRESHOLD_PX = 50;

  // ── Inject the reveal transition styles once. ──
  function injectStepItemStyles() {
    const style = document.createElement('style');
    style.textContent = `
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
  }

  function getActiveSlide() {
    return document.querySelector('.slide.on');
  }

  function getHiddenStepItems(slide) {
    return slide ? slide.querySelectorAll('.step-item:not(.show)') : [];
  }

  /**
   * Reveals the next hidden step-item on the active slide, if any.
   * @returns {boolean} true if an item was revealed (caller should block
   *   the slide from advancing); false if there's nothing left to reveal.
   */
  function revealNextStepItem() {
    const activeSlide = getActiveSlide();
    if (!activeSlide) return false;

    const hidden = getHiddenStepItems(activeSlide);
    if (hidden.length === 0) return false;

    hidden[0].classList.add('show');
    return true;
  }

  function activeSlideHasHiddenSteps() {
    const activeSlide = getActiveSlide();
    return !!activeSlide && getHiddenStepItems(activeSlide).length > 0;
  }

  // ── Keyboard navigation: intercept "forward" keys while steps remain. ──
  const FORWARD_KEYS = new Set(['ArrowRight', 'ArrowDown', ' ', 'PageDown']);

  function isTextInputTarget(el) {
    return el.tagName === 'INPUT' || el.tagName === 'TEXTAREA';
  }

  function handleKeydown(e) {
    if (isTextInputTarget(e.target)) return;
    if (!FORWARD_KEYS.has(e.key)) return;
    if (!activeSlideHasHiddenSteps()) return;

    e.preventDefault();
    e.stopImmediatePropagation(); // Prevent the deck's own slide-advance handler.
    revealNextStepItem();
  }

  // ── Click navigation: Next button or clicking the deck itself. ──
  const CLICK_EXCLUDE_SELECTOR = '#navPrev, .dots, .fs-btn, a';
  const CLICK_ADVANCE_SELECTOR = '#navNext, #deck';

  function handleClick(e) {
    if (e.target.closest(CLICK_EXCLUDE_SELECTOR)) return;
    if (!e.target.closest(CLICK_ADVANCE_SELECTOR)) return;
    if (!activeSlideHasHiddenSteps()) return;

    e.preventDefault();
    e.stopImmediatePropagation();
    revealNextStepItem();
  }

  // ── Touch navigation: swipe left to advance. ──
  let touchStartX = null;

  function handleTouchStart(e) {
    touchStartX = e.changedTouches[0].clientX;
  }

  function handleTouchEnd(e) {
    if (touchStartX === null) return;

    const deltaX = e.changedTouches[0].clientX - touchStartX;
    touchStartX = null;

    const isSwipeLeft = deltaX < -SWIPE_THRESHOLD_PX;
    if (isSwipeLeft && activeSlideHasHiddenSteps()) {
      e.stopImmediatePropagation();
      revealNextStepItem();
    }
  }

  // ── Track slide transitions to reset/reveal step-items appropriately. ──
  let lastSlideIndex = 0;

  function handleSlideClassMutation(mutation) {
    const target = mutation.target;
    if (!target.classList.contains('on')) return;

    const slides = Array.from(document.querySelectorAll('.slide'));
    const newIndex = slides.indexOf(target);
    if (newIndex === -1) return;

    if (newIndex > lastSlideIndex) {
      // Moving forward: hide step-items so they reveal one-by-one again.
      target.querySelectorAll('.step-item').forEach((el) => el.classList.remove('show'));
    } else if (newIndex < lastSlideIndex) {
      // Moving backward: show everything immediately (no re-clicking needed).
      target.querySelectorAll('.step-item').forEach((el) => el.classList.add('show'));
    }
    lastSlideIndex = newIndex;
  }

  function observeSlideTransitions() {
    const observer = new MutationObserver((mutations) => {
      mutations.forEach((mutation) => {
        if (mutation.attributeName === 'class') {
          handleSlideClassMutation(mutation);
        }
      });
    });

    document.querySelectorAll('.slide').forEach((slide) => {
      observer.observe(slide, { attributes: true, attributeFilter: ['class'] });
    });
  }

  // ── Initial setup once the DOM is ready. ──
  function markStepItems() {
    document.querySelectorAll(STEP_ITEM_SELECTOR).forEach((el) => {
      el.classList.add('step-item');
    });
  }

  function hideStepItemsOnFirstSlide() {
    // Deferred slightly so any other init logic (e.g. deck bootstrapping)
    // has already marked the first slide as active.
    setTimeout(() => {
      const firstSlide = getActiveSlide();
      if (firstSlide) {
        firstSlide.querySelectorAll('.step-item').forEach((el) => el.classList.remove('show'));
      }
    }, 100);
  }

  function init() {
    injectStepItemStyles();
    markStepItems();
    observeSlideTransitions();
    hideStepItemsOnFirstSlide();

    document.addEventListener('keydown', handleKeydown, true);
    document.addEventListener('click', handleClick, true);
    document.addEventListener('touchstart', handleTouchStart, { passive: true, capture: true });
    document.addEventListener('touchend', handleTouchEnd, true);
  }

  document.addEventListener('DOMContentLoaded', init);
})();