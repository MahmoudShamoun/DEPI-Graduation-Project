/**
 * Step-by-step reveal controller for the Gold Egypt presentation deck.
 *
 * Elements marked with the `.step-item` class inside the active slide are
 * revealed one at a time (via keyboard, click, or swipe) before the deck is
 * allowed to advance to the next slide. This is what turns a single slide
 * carrying "Question / Chart / Insight" into a progressive reveal: the
 * question text animates in immediately with the slide, then the chart
 * (`.iframe-wrap`) and insight (`.q-insight`) each require one more
 * "next" action to appear.
 *
 * Navigating backward reveals all step-items on the target slide
 * immediately, so the presenter never has to re-click through content
 * they've already shown.
 *
 * Public surface: none. This file is a self-contained IIFE; it only
 * listens on `document` and mutates DOM classes, so it composes safely
 * with the deck-navigation script inline in index.html.
 */
(function () {
  'use strict';

  // ── Config ────────────────────────────────────────────────────────────
  const CONFIG = {
    // Selectors for elements revealed step-by-step. Slide titles/subtitles
    // are intentionally excluded — they animate in immediately via CSS
    // when a slide becomes active.
    stepItemSelector: [
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
    ].join(',\n'),
    swipeThresholdPx: 50,
    forwardKeys: new Set(['ArrowRight', 'ArrowDown', ' ', 'PageDown']),
    clickExcludeSelector: '#navPrev, .dots, .fs-btn, a',
    clickAdvanceSelector: '#navNext, #deck',
    revealTransitionMs: 400,
  };

  // ── Small DOM helpers ─────────────────────────────────────────────────
  const dom = {
    activeSlide: () => document.querySelector('.slide.on'),
    allSlides: () => Array.from(document.querySelectorAll('.slide')),
    hiddenStepItems: (slide) =>
      slide ? slide.querySelectorAll('.step-item:not(.show)') : [],
    isTextInput: (el) => el.tagName === 'INPUT' || el.tagName === 'TEXTAREA',
  };

  // ── State ─────────────────────────────────────────────────────────────
  const state = {
    lastSlideIndex: 0,
    touchStartX: null,
  };

  // ── Styles (injected once) ───────────────────────────────────────────
  function injectStepItemStyles() {
    const style = document.createElement('style');
    style.dataset.source = 'main.js:step-reveal';
    style.textContent = `
      .step-item {
        opacity: 0;
        transform: translateY(15px);
        transition: opacity ${CONFIG.revealTransitionMs}ms ease-out,
                    transform ${CONFIG.revealTransitionMs}ms ease-out;
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

  // ── Core reveal logic ────────────────────────────────────────────────

  /**
   * Reveals the next hidden step-item on the active slide, if any.
   * @returns {boolean} true if an item was revealed (caller should block
   *   the slide from advancing); false if there's nothing left to reveal.
   */
  function revealNextStepItem() {
    const activeSlide = dom.activeSlide();
    if (!activeSlide) return false;

    const hidden = dom.hiddenStepItems(activeSlide);
    if (hidden.length === 0) return false;

    hidden[0].classList.add('show');
    return true;
  }

  function activeSlideHasHiddenSteps() {
    const activeSlide = dom.activeSlide();
    return !!activeSlide && dom.hiddenStepItems(activeSlide).length > 0;
  }

  function revealAllStepsOn(slide) {
    slide.querySelectorAll('.step-item').forEach((el) => el.classList.add('show'));
  }

  function hideAllStepsOn(slide) {
    slide.querySelectorAll('.step-item').forEach((el) => el.classList.remove('show'));
  }

  // ── Input handlers ────────────────────────────────────────────────────
  function handleKeydown(e) {
    if (dom.isTextInput(e.target)) return;
    if (!CONFIG.forwardKeys.has(e.key)) return;
    if (!activeSlideHasHiddenSteps()) return;

    e.preventDefault();
    e.stopImmediatePropagation(); // Block the deck's own slide-advance handler.
    revealNextStepItem();
  }

  function handleClick(e) {
    if (e.target.closest(CONFIG.clickExcludeSelector)) return;
    if (!e.target.closest(CONFIG.clickAdvanceSelector)) return;
    if (!activeSlideHasHiddenSteps()) return;

    e.preventDefault();
    e.stopImmediatePropagation();
    revealNextStepItem();
  }

  function handleTouchStart(e) {
    state.touchStartX = e.changedTouches[0].clientX;
  }

  function handleTouchEnd(e) {
    if (state.touchStartX === null) return;

    const deltaX = e.changedTouches[0].clientX - state.touchStartX;
    state.touchStartX = null;

    const isSwipeLeft = deltaX < -CONFIG.swipeThresholdPx;
    if (isSwipeLeft && activeSlideHasHiddenSteps()) {
      e.stopImmediatePropagation();
      revealNextStepItem();
    }
  }

  // ── Slide-transition tracking ─────────────────────────────────────────
  function handleSlideClassMutation(mutation) {
    const target = mutation.target;
    if (!target.classList.contains('on')) return;

    const slides = dom.allSlides();
    const newIndex = slides.indexOf(target);
    if (newIndex === -1) return;

    if (newIndex > state.lastSlideIndex) {
      // Moving forward: hide step-items so they reveal one-by-one again.
      hideAllStepsOn(target);
    } else if (newIndex < state.lastSlideIndex) {
      // Moving backward: show everything immediately (no re-clicking needed).
      revealAllStepsOn(target);
    }
    state.lastSlideIndex = newIndex;
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

  // ── Initial setup ─────────────────────────────────────────────────────
  function markStepItems() {
    document.querySelectorAll(CONFIG.stepItemSelector).forEach((el) => {
      el.classList.add('step-item');
    });
  }

  function hideStepItemsOnFirstSlide() {
    // Deferred slightly so any other init logic (e.g. deck bootstrapping)
    // has already marked the first slide as active.
    setTimeout(() => {
      const firstSlide = dom.activeSlide();
      if (firstSlide) hideAllStepsOn(firstSlide);
    }, 100);
  }

  function bindEventListeners() {
    document.addEventListener('keydown', handleKeydown, true);
    document.addEventListener('click', handleClick, true);
    document.addEventListener('touchstart', handleTouchStart, { passive: true, capture: true });
    document.addEventListener('touchend', handleTouchEnd, true);
  }

  function init() {
    injectStepItemStyles();
    markStepItems();
    observeSlideTransitions();
    hideStepItemsOnFirstSlide();
    bindEventListeners();
  }

  document.addEventListener('DOMContentLoaded', init);
})();