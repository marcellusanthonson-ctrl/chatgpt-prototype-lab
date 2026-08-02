(function (global) {
  'use strict';

  const DEFAULTS = Object.freeze({
    root: '[data-roadmap]',
    timeline: '[data-roadmap-timeline]',
    line: '[data-roadmap-line]',
    progress: '[data-roadmap-progress]',
    step: '[data-roadmap-step]',
    dot: '[data-roadmap-dot]',
    card: '[data-roadmap-card]',
    triggerRatio: 0.64,
    bottomSafetyGap: 72,
    releaseMargin: 16,
    dotActivationOffset: 3,
    endTolerance: 2,
    minimumRailHeight: 1,
    revealThreshold: 0.1,
    revealRootMargin: '0px',
    settleDelays: [120, 360],
    stableSamplesRequired: 3,
    maximumStabilizationFrames: 12,
    classes: Object.freeze({
      visible: 'is-visible',
      dotActive: 'is-dot-active',
      endActive: 'is-end-active'
    }),
    variables: Object.freeze({
      railStart: '--rail-start',
      railHeight: '--rail-height',
      railFillHeight: '--rail-fill-height',
      stepProgress: '--progress'
    })
  });

  const clamp = (value, minimum, maximum) => Math.min(Math.max(value, minimum), maximum);
  const finite = (value, fallback) => Number.isFinite(value) ? value : fallback;
  const rounded = value => Math.round(value * 100) / 100;

  function mergeOptions(options) {
    const input = options || {};
    return {
      ...DEFAULTS,
      ...input,
      classes: { ...DEFAULTS.classes, ...(input.classes || {}) },
      variables: { ...DEFAULTS.variables, ...(input.variables || {}) },
      settleDelays: Array.isArray(input.settleDelays) ? [...input.settleDelays] : [...DEFAULTS.settleDelays]
    };
  }

  class RoadmapProgressCore {
    constructor(options) {
      this.options = mergeOptions(options);
      this.root = null;
      this.timeline = null;
      this.line = null;
      this.progress = null;
      this.steps = [];
      this.dots = [];
      this.cards = [];
      this.geometry = null;
      this.connected = false;
      this.destroyed = false;
      this.measureQueued = false;
      this.updateQueued = false;
      this.measurementInProgress = false;
      this.measurementRequestedAgain = false;
      this.stableSamples = 0;
      this.stabilizationFrames = 0;
      this.lastMeasurementSignature = '';
      this.cleanup = [];
      this.resizeObserver = null;
      this.intersectionObserver = null;
      this.reduceQuery = null;
      this.reducedMotion = false;
      this.lastState = null;
    }

    resolveRoot() {
      const value = this.options.root;
      if (value && value.nodeType === 1) return value;
      if (typeof value === 'string') return document.querySelector(value);
      return null;
    }

    query(scope, selector) {
      if (!scope || !selector) return null;
      if (selector && selector.nodeType === 1) return selector;
      return typeof selector === 'string' ? scope.querySelector(selector) : null;
    }

    queryAll(scope, selector) {
      if (!scope || !selector) return [];
      if (Array.isArray(selector)) return selector.filter(item => item && item.nodeType === 1);
      return typeof selector === 'string' ? Array.from(scope.querySelectorAll(selector)) : [];
    }

    resolveElements() {
      this.root = this.resolveRoot();
      this.timeline = this.query(this.root, this.options.timeline);
      this.line = this.query(this.timeline, this.options.line);
      this.progress = this.query(this.timeline, this.options.progress);
      this.steps = this.queryAll(this.timeline, this.options.step);
      this.dots = this.steps.map(step => this.query(step, this.options.dot));
      this.cards = this.steps.map(step => this.query(step, this.options.card));
      return Boolean(
        this.root && this.timeline && this.line && this.progress &&
        this.steps.length && this.dots.every(Boolean) && this.cards.every(Boolean)
      );
    }

    connect() {
      if (this.connected || this.destroyed) return this;
      if (!this.resolveElements()) return this;
      this.connected = true;

      this.reduceQuery = window.matchMedia ? window.matchMedia('(prefers-reduced-motion: reduce)') : null;
      this.reducedMotion = Boolean(this.reduceQuery && this.reduceQuery.matches);

      const requestMeasure = () => this.requestMeasure('environment');
      const requestUpdate = () => this.requestUpdate();
      window.addEventListener('scroll', requestUpdate, { passive: true });
      window.addEventListener('resize', requestMeasure, { passive: true });
      window.addEventListener('orientationchange', requestMeasure, { passive: true });
      window.addEventListener('load', requestMeasure, { passive: true });
      this.cleanup.push(() => window.removeEventListener('scroll', requestUpdate));
      this.cleanup.push(() => window.removeEventListener('resize', requestMeasure));
      this.cleanup.push(() => window.removeEventListener('orientationchange', requestMeasure));
      this.cleanup.push(() => window.removeEventListener('load', requestMeasure));

      if (this.reduceQuery) {
        const onReduce = event => {
          this.reducedMotion = Boolean(event.matches);
          this.revealForReducedMotion();
          this.requestMeasure('reduced-motion-change');
        };
        if (this.reduceQuery.addEventListener) {
          this.reduceQuery.addEventListener('change', onReduce);
          this.cleanup.push(() => this.reduceQuery.removeEventListener('change', onReduce));
        } else if (this.reduceQuery.addListener) {
          this.reduceQuery.addListener(onReduce);
          this.cleanup.push(() => this.reduceQuery.removeListener(onReduce));
        }
      }

      this.setupRevealObserver();
      this.setupResizeObserver();

      if (document.fonts && document.fonts.ready) {
        document.fonts.ready.then(() => this.requestMeasure('fonts-ready')).catch(() => {});
      }

      for (const delay of this.options.settleDelays) {
        const timer = window.setTimeout(() => this.requestMeasure(`settle-${delay}`), Math.max(0, delay));
        this.cleanup.push(() => window.clearTimeout(timer));
      }

      this.revealForReducedMotion();
      this.requestMeasure('connect');
      return this;
    }

    disconnect() {
      if (!this.connected) return this;
      this.connected = false;
      for (const dispose of this.cleanup.splice(0)) {
        try { dispose(); } catch (_) {}
      }
      if (this.resizeObserver) this.resizeObserver.disconnect();
      if (this.intersectionObserver) this.intersectionObserver.disconnect();
      this.resizeObserver = null;
      this.intersectionObserver = null;
      return this;
    }

    destroy() {
      this.disconnect();
      this.destroyed = true;
      return this;
    }

    setupRevealObserver() {
      const visibleClass = this.options.classes.visible;
      if (this.reducedMotion || typeof IntersectionObserver !== 'function') {
        this.steps.forEach(step => step.classList.add(visibleClass));
        return;
      }
      this.intersectionObserver = new IntersectionObserver((entries, observer) => {
        for (const entry of entries) {
          if (entry.isIntersecting) {
            entry.target.classList.add(visibleClass);
            observer.unobserve(entry.target);
          }
        }
      }, {
        root: null,
        rootMargin: this.options.revealRootMargin,
        threshold: this.options.revealThreshold
      });
      this.steps.forEach(step => this.intersectionObserver.observe(step));
    }

    revealForReducedMotion() {
      if (!this.reducedMotion) return;
      this.steps.forEach(step => step.classList.add(this.options.classes.visible));
    }

    setupResizeObserver() {
      if (typeof ResizeObserver !== 'function') return;
      this.resizeObserver = new ResizeObserver(() => {
        if (!this.measurementInProgress) this.requestMeasure('resize-observer');
      });
      this.resizeObserver.observe(this.timeline);
      this.dots.forEach(dot => this.resizeObserver.observe(dot));
      this.cards.forEach(card => this.resizeObserver.observe(card));
    }

    requestMeasure() {
      if (!this.connected || this.destroyed) return;
      if (this.measurementInProgress) {
        this.measurementRequestedAgain = true;
        return;
      }
      if (this.measureQueued) return;
      this.measureQueued = true;
      requestAnimationFrame(() => {
        this.measureQueued = false;
        this.measure();
      });
    }

    requestUpdate() {
      if (!this.connected || this.destroyed || this.updateQueued) return;
      this.updateQueued = true;
      requestAnimationFrame(() => {
        this.updateQueued = false;
        this.update();
      });
    }

    centerInTimeline(element, timelineRect) {
      const rect = element.getBoundingClientRect();
      return rect.top + rect.height / 2 - timelineRect.top;
    }

    getDocumentHeight() {
      const body = document.body;
      const html = document.documentElement;
      return Math.max(
        body ? body.scrollHeight : 0,
        body ? body.offsetHeight : 0,
        html ? html.clientHeight : 0,
        html ? html.scrollHeight : 0,
        html ? html.offsetHeight : 0
      );
    }

    setTrailingPadding(value) {
      const pixels = Math.max(0, Math.ceil(finite(value, 0)));
      this.timeline.style.paddingBottom = `${pixels}px`;
      return pixels;
    }

    calculateGeometry(basePadding) {
      const initialRect = this.timeline.getBoundingClientRect();
      const firstDotCenter = this.centerInTimeline(this.dots[0], initialRect);
      const lastCard = this.cards[this.cards.length - 1];
      const lastCardRect = lastCard.getBoundingClientRect();
      const lastCardHeight = Math.max(1, finite(lastCardRect.height, 280));

      const minimumPadding = Math.ceil(lastCardHeight + this.options.bottomSafetyGap);
      const appliedBasePadding = this.setTrailingPadding(Math.max(basePadding || 0, minimumPadding));
      const remeasuredRect = this.timeline.getBoundingClientRect();
      const remeasuredCardRect = lastCard.getBoundingClientRect();
      const lastCardTop = remeasuredCardRect.top - remeasuredRect.top;
      const lastCardMid = lastCardTop + lastCardHeight / 2;
      const targetTailEnd = lastCardMid + lastCardHeight;
      const railStart = Math.max(0, firstDotCenter);
      const railEnd = Math.min(remeasuredRect.height, targetTailEnd);
      const railHeight = Math.max(this.options.minimumRailHeight, railEnd - railStart);

      const timelineDocumentTop = remeasuredRect.top + window.scrollY;
      const triggerY = window.innerHeight * this.options.triggerRatio;
      const requiredDocumentHeight = timelineDocumentTop + railEnd + window.innerHeight - triggerY + this.options.releaseMargin;
      const currentDocumentHeight = this.getDocumentHeight();
      const additionalPadding = Math.max(0, Math.ceil(requiredDocumentHeight - currentDocumentHeight));
      const finalPadding = additionalPadding > 0 ? this.setTrailingPadding(appliedBasePadding + additionalPadding) : appliedBasePadding;

      const finalRect = this.timeline.getBoundingClientRect();
      const finalCardRect = lastCard.getBoundingClientRect();
      const finalCardTop = finalCardRect.top - finalRect.top;
      const finalCardMid = finalCardTop + lastCardHeight / 2;
      const finalTailEnd = finalCardMid + lastCardHeight;
      const finalRailEnd = Math.min(finalRect.height, finalTailEnd);
      const finalRailHeight = Math.max(this.options.minimumRailHeight, finalRailEnd - railStart);

      const stepGeometry = this.steps.map((step, index) => {
        const stepRect = step.getBoundingClientRect();
        const dotOffset = this.centerInTimeline(this.dots[index], finalRect) - railStart;
        const stepTop = stepRect.top - finalRect.top - railStart;
        const stepBottom = stepRect.bottom - finalRect.top - railStart;
        return {
          dotOffset,
          stepTop,
          stepDistance: Math.max(1, stepBottom - stepTop)
        };
      });

      return {
        railStart,
        railEnd: finalRailEnd,
        railHeight: finalRailHeight,
        paddingBottom: finalPadding,
        minimumPadding,
        additionalPadding,
        releaseMargin: this.options.releaseMargin,
        timelineDocumentTop: finalRect.top + window.scrollY,
        stepGeometry
      };
    }

    measure() {
      if (!this.connected || this.destroyed) return;
      this.measurementInProgress = true;
      this.measurementRequestedAgain = false;
      try {
        const geometry = this.calculateGeometry(0);
        const signature = JSON.stringify([
          rounded(geometry.railStart),
          rounded(geometry.railHeight),
          geometry.paddingBottom,
          rounded(window.innerWidth),
          rounded(window.innerHeight),
          ...geometry.stepGeometry.flatMap(item => [rounded(item.dotOffset), rounded(item.stepTop), rounded(item.stepDistance)])
        ]);
        if (signature === this.lastMeasurementSignature) {
          this.stableSamples += 1;
        } else {
          this.lastMeasurementSignature = signature;
          this.stableSamples = 1;
        }
        this.geometry = geometry;
        this.timeline.style.setProperty(this.options.variables.railStart, `${geometry.railStart.toFixed(2)}px`);
        this.timeline.style.setProperty(this.options.variables.railHeight, `${geometry.railHeight.toFixed(2)}px`);
        this.update();
      } finally {
        this.measurementInProgress = false;
      }

      const stable = this.stableSamples >= this.options.stableSamplesRequired;
      if ((!stable && this.stabilizationFrames < this.options.maximumStabilizationFrames) || this.measurementRequestedAgain) {
        this.stabilizationFrames += 1;
        this.requestMeasure('stabilize');
      } else {
        this.stabilizationFrames = 0;
      }
    }

    update() {
      if (!this.connected || !this.geometry) return;
      const rect = this.timeline.getBoundingClientRect();
      const triggerY = window.innerHeight * this.options.triggerRatio;
      let fillHeight = clamp(triggerY - rect.top - this.geometry.railStart, 0, this.geometry.railHeight);
      if (this.reducedMotion) fillHeight = this.geometry.railHeight;

      const endActive = fillHeight >= this.geometry.railHeight - this.options.endTolerance;
      this.timeline.style.setProperty(this.options.variables.railFillHeight, `${fillHeight.toFixed(2)}px`);
      this.timeline.classList.toggle(this.options.classes.endActive, endActive);

      const stepsState = this.steps.map((step, index) => {
        const item = this.geometry.stepGeometry[index];
        const dotActive = this.reducedMotion || fillHeight >= item.dotOffset + this.options.dotActivationOffset;
        const progress = this.reducedMotion ? 1 : clamp((fillHeight - item.stepTop) / item.stepDistance, 0, 1);
        step.classList.toggle(this.options.classes.dotActive, dotActive);
        step.style.setProperty(this.options.variables.stepProgress, progress.toFixed(3));
        if (this.reducedMotion) step.classList.add(this.options.classes.visible);
        return {
          dotActive,
          progress,
          visible: step.classList.contains(this.options.classes.visible)
        };
      });

      this.lastState = {
        fillHeight,
        fillRatio: this.geometry.railHeight > 0 ? fillHeight / this.geometry.railHeight : 1,
        endActive,
        reducedMotion: this.reducedMotion,
        geometry: { ...this.geometry },
        steps: stepsState,
        scrollTop: window.scrollY,
        maxScroll: Math.max(0, this.getDocumentHeight() - window.innerHeight)
      };

      this.root.dispatchEvent(new CustomEvent('roadmapprogresschange', { detail: this.getState() }));
    }

    getState() {
      if (!this.lastState) return null;
      return JSON.parse(JSON.stringify(this.lastState));
    }
  }

  function createRoadmapProgressCore(options) {
    return new RoadmapProgressCore(options);
  }

  const api = Object.freeze({ RoadmapProgressCore, createRoadmapProgressCore, defaults: DEFAULTS });
  if (typeof module !== 'undefined' && module.exports) module.exports = api;
  global.RoadmapProgressCore = api;
})(typeof window !== 'undefined' ? window : globalThis);
