(function () {
  'use strict';

  const state = {
    hasTriggered: false,
    isAnimating: false,
    isComplete: false,
    isReducedMotion: false,
    speed: 1,
    animationFrameIds: new Set(),
    timeoutIds: new Set(),
    observer: null,
    runToken: 0
  };

  const elements = {};
  const pillarSteps = ['Audición', 'Audición, Lenguaje', 'Audición, Lenguaje y TDAH'];

  function scaled(milliseconds) {
    return milliseconds / state.speed;
  }

  function schedule(callback, milliseconds, token) {
    const id = window.setTimeout(function () {
      state.timeoutIds.delete(id);
      if (token === state.runToken) callback();
    }, scaled(milliseconds));
    state.timeoutIds.add(id);
    return id;
  }

  function updateStatus(label) {
    if (elements.status) elements.status.textContent = label;
  }

  function cancelActiveAnimations() {
    state.runToken += 1;
    state.animationFrameIds.forEach(function (id) { window.cancelAnimationFrame(id); });
    state.timeoutIds.forEach(function (id) { window.clearTimeout(id); });
    state.animationFrameIds.clear();
    state.timeoutIds.clear();
    state.isAnimating = false;
  }

  function setPortalVisible(count) {
    elements.portalBase.textContent = '24';
    elements.portalSuffix.textContent = count >= 3 ? '/7' : count >= 2 ? '/' : '';
  }

  function resetVisualState() {
    document.documentElement.classList.remove('motion-disabled');
    elements.patients.textContent = '0';
    elements.years.textContent = '0';
    elements.pillars.textContent = pillarSteps[0];
    setPortalVisible(0);
    state.isComplete = false;
  }

  function showFinalState(statusLabel) {
    cancelActiveAnimations();
    document.documentElement.classList.toggle('motion-disabled', statusLabel === 'Movimiento reducido');
    elements.patients.textContent = '1000';
    elements.years.textContent = '28';
    elements.pillars.textContent = pillarSteps[2];
    setPortalVisible(3);
    state.isComplete = true;
    updateStatus('Estado final canónico');
  }

  function easeOutCubic(progress) {
    return 1 - Math.pow(1 - progress, 3);
  }

  function animateInteger(element, target, delay, duration, token) {
    schedule(function () {
      const startTime = performance.now();

      function frame(now) {
        if (token !== state.runToken) return;
        const progress = Math.min((now - startTime) / scaled(duration), 1);
        const value = Math.min(target, Math.round(target * easeOutCubic(progress)));
        element.textContent = String(value);

        if (progress < 1) {
          const id = window.requestAnimationFrame(function (nextNow) {
            state.animationFrameIds.delete(id);
            frame(nextNow);
          });
          state.animationFrameIds.add(id);
        } else {
          element.textContent = String(target);
        }
      }

      frame(performance.now());
    }, delay, token);
  }

  function animatePillars(token) {
    pillarSteps.forEach(function (text, index) {
      schedule(function () {
        elements.pillars.textContent = text;
        const id = window.requestAnimationFrame(function () {
          state.animationFrameIds.delete(id);
          if (token === state.runToken) elements.pillars.textContent = text;
        });
        state.animationFrameIds.add(id);
      }, 200 + (index * 205), token);
    });
  }

  function animatePortalAvailability(token) {
    [1, 2, 3].forEach(function (visibleCount, index) {
      schedule(function () { setPortalVisible(visibleCount); }, 320 + (index * 180), token);
    });
  }

  function startSequence() {
    if (state.isReducedMotion) {
      showFinalState('Movimiento reducido');
      return;
    }

    cancelActiveAnimations();
    resetVisualState();
    state.isAnimating = true;
    updateStatus('Animación en curso');
    const token = state.runToken;

    animateInteger(elements.patients, 1000, 0, 1600, token);
    animateInteger(elements.years, 28, 100, 1250, token);
    animatePillars(token);
    animatePortalAvailability(token);
    schedule(function () {
      elements.patients.textContent = '1000';
      elements.years.textContent = '28';
      elements.pillars.textContent = pillarSteps[2];
      setPortalVisible(3);
      state.isAnimating = false;
      state.isComplete = true;
      updateStatus('Estado final canónico');
    }, 1800, token);
  }

  function resetExperiment() {
    cancelActiveAnimations();
    resetVisualState();
    if (state.isReducedMotion) {
      showFinalState('Movimiento reducido');
    } else {
      state.hasTriggered = true;
      startSequence();
    }
  }

  function applyReducedMotionState(isReduced) {
    state.isReducedMotion = isReduced;
    if (isReduced) {
      showFinalState('Movimiento reducido');
    } else {
      cancelActiveAnimations();
      resetVisualState();
      updateStatus('Listo para animar');
    }
  }

  function createObserver() {
    if (!('IntersectionObserver' in window)) {
      showFinalState('Completado');
      return;
    }

    state.observer = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting && entry.intersectionRatio >= 0.4 && !state.hasTriggered) {
          state.hasTriggered = true;
          state.observer.disconnect();
          startSequence();
        }
      });
    }, { threshold: [0.4] });

    state.observer.observe(elements.section);
  }

  function cacheElements() {
    elements.section = document.querySelector('.stats-grid');
    elements.cells = Array.from(document.querySelectorAll('.stat-cell'));
    elements.numbers = elements.cells.map(function (cell) { return cell.querySelector('.stat-num'); });
    elements.labels = elements.cells.map(function (cell) { return cell.querySelector('.stat-lbl'); });
    elements.patients = elements.numbers[0] && elements.numbers[0].querySelector('.stat-number');
    elements.years = elements.numbers[1];
    elements.pillars = elements.labels[2] && elements.labels[2].querySelector('br') &&
      elements.labels[2].querySelector('br').nextSibling;
    elements.portalBase = elements.numbers[3] && elements.numbers[3].firstChild;
    elements.portalSuffix = elements.numbers[3] && elements.numbers[3].querySelector('.plus');
    elements.reset = document.querySelector('[data-exp005-action="replay"]');
    elements.final = document.querySelector('[data-exp005-action="final"]');
    elements.reduced = document.querySelector('[data-exp005-action="reduced"]');
    elements.status = document.querySelector('.exp005-status');

    return Boolean(
      elements.section && elements.cells.length === 4 && elements.numbers.every(Boolean) &&
      elements.labels.every(Boolean) && elements.patients &&
      elements.patients.nodeType === Node.ELEMENT_NODE && elements.years && elements.pillars &&
      elements.pillars.nodeType === Node.TEXT_NODE && elements.portalBase &&
      elements.portalBase.nodeType === Node.TEXT_NODE && elements.portalSuffix &&
      elements.reset && elements.final && elements.reduced && elements.status
    );
  }

  function initializeExperiment() {
    if (!cacheElements()) return;

    resetVisualState();
    const nativeReducedQuery = window.matchMedia('(prefers-reduced-motion: reduce)');
    const simulatedReduced = elements.reduced.getAttribute('aria-pressed') === 'true';
    state.isReducedMotion = nativeReducedQuery.matches || simulatedReduced;

    elements.reset.addEventListener('click', resetExperiment);
    elements.final.addEventListener('click', function () { showFinalState('Completado'); });
    elements.reduced.addEventListener('click', function () {
      const nextReduced = elements.reduced.getAttribute('aria-pressed') !== 'true';
      elements.reduced.setAttribute('aria-pressed', String(nextReduced));
      elements.reduced.textContent = nextReduced ? 'Movimiento reducido: sí' : 'Movimiento reducido: no';
      applyReducedMotionState(nativeReducedQuery.matches || nextReduced);
    });

    const handleNativeMotionChange = function (event) {
      const simulated = elements.reduced.getAttribute('aria-pressed') === 'true';
      applyReducedMotionState(event.matches || simulated);
    };
    if (typeof nativeReducedQuery.addEventListener === 'function') {
      nativeReducedQuery.addEventListener('change', handleNativeMotionChange);
    } else if (typeof nativeReducedQuery.addListener === 'function') {
      nativeReducedQuery.addListener(handleNativeMotionChange);
    }

    if (state.isReducedMotion) {
      showFinalState('Movimiento reducido');
    } else {
      updateStatus('Listo para animar');
      createObserver();
    }
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', function () {
      document.fonts.ready.then(initializeExperiment);
    }, { once: true });
  } else {
    document.fonts.ready.then(initializeExperiment);
  }
}());
