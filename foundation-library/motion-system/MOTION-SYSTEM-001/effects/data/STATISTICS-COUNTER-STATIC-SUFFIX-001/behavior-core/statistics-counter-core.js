(function (global) {
  'use strict';

  const DEFAULTS = Object.freeze({
    root: null,
    threshold: 0.4,
    once: true,
    autoConnect: false,
    reducedMotionQuery: '(prefers-reduced-motion: reduce)',
    completionPaddingMs: 0,
    eventName: 'statisticscounterchange'
  });

  const clamp = (value, minimum, maximum) => Math.min(Math.max(value, minimum), maximum);
  const identity = value => String(value);
  const easeOutCubic = progress => 1 - Math.pow(1 - progress, 3);

  function resolveElement(value, scope) {
    if (!value) return null;
    if (value.nodeType === 1 || value.nodeType === 3) return value;
    if (typeof value === 'string' && scope && typeof scope.querySelector === 'function') {
      return scope.querySelector(value);
    }
    return null;
  }

  function normalizeNumericTarget(input, scope) {
    const element = resolveElement(input.element || input.selector, scope);
    if (!element) throw new Error('Numeric target element could not be resolved.');
    const from = Number.isFinite(input.from) ? input.from : 0;
    const to = Number(input.to);
    if (!Number.isFinite(to)) throw new Error('Numeric target requires a finite `to` value.');
    return {
      id: input.id || null,
      type: 'numeric',
      element,
      from,
      to,
      delay: Math.max(0, Number(input.delay) || 0),
      duration: Math.max(0, Number(input.duration) || 0),
      easing: typeof input.easing === 'function' ? input.easing : easeOutCubic,
      formatter: typeof input.formatter === 'function' ? input.formatter : identity,
      finalText: null
    };
  }

  function normalizeSequenceTarget(input, scope) {
    const element = resolveElement(input.element || input.selector, scope);
    if (!element) throw new Error('Sequence target element could not be resolved.');
    const values = Array.isArray(input.values) ? input.values.map(String) : [];
    if (!values.length) throw new Error('Sequence target requires at least one value.');
    return {
      id: input.id || null,
      type: 'sequence',
      element,
      values,
      delay: Math.max(0, Number(input.delay) || 0),
      stepMs: Math.max(0, Number(input.stepMs) || 0),
      finalText: values[values.length - 1]
    };
  }

  function normalizeTarget(input, scope) {
    if (!input || typeof input !== 'object') throw new Error('Target descriptor must be an object.');
    return input.type === 'sequence'
      ? normalizeSequenceTarget(input, scope)
      : normalizeNumericTarget(input, scope);
  }

  function mergeOptions(options) {
    return { ...DEFAULTS, ...(options || {}) };
  }

  class StatisticsCounterCore {
    constructor(options) {
      this.options = mergeOptions(options);
      this.root = null;
      this.targets = [];
      this.connected = false;
      this.destroyed = false;
      this.triggered = false;
      this.running = false;
      this.complete = false;
      this.reducedMotion = false;
      this.runToken = 0;
      this.animationFrameIds = new Set();
      this.timeoutIds = new Set();
      this.cleanup = [];
      this.observer = null;
      this.mediaQuery = null;
      this.lastState = null;
      this.initialNodeIdentities = [];
      if (this.options.autoConnect) this.connect();
    }

    now() {
      return this.options.now ? this.options.now() : global.performance.now();
    }

    requestFrame(callback) {
      const request = this.options.requestAnimationFrame || global.requestAnimationFrame.bind(global);
      return request(callback);
    }

    cancelFrame(id) {
      const cancel = this.options.cancelAnimationFrame || global.cancelAnimationFrame.bind(global);
      cancel(id);
    }

    setTimer(callback, delay) {
      const set = this.options.setTimeout || global.setTimeout.bind(global);
      return set(callback, delay);
    }

    clearTimer(id) {
      const clear = this.options.clearTimeout || global.clearTimeout.bind(global);
      clear(id);
    }

    resolveRoot() {
      const value = this.options.root;
      if (value && value.nodeType === 1) return value;
      if (typeof value === 'string' && global.document) return global.document.querySelector(value);
      return global.document || null;
    }

    resolveTargets() {
      const descriptors = Array.isArray(this.options.targets) ? this.options.targets : [];
      this.targets = descriptors.map(item => normalizeTarget(item, this.root));
      this.initialNodeIdentities = this.targets.map(target => target.element);
      return this.targets.length > 0;
    }

    connect() {
      if (this.connected || this.destroyed) return this;
      this.root = this.resolveRoot();
      if (!this.root || !this.resolveTargets()) return this;
      this.connected = true;

      const matchMedia = this.options.matchMedia || (global.matchMedia ? global.matchMedia.bind(global) : null);
      this.mediaQuery = matchMedia ? matchMedia(this.options.reducedMotionQuery) : null;
      this.reducedMotion = Boolean(this.mediaQuery && this.mediaQuery.matches);

      if (this.mediaQuery) {
        const onChange = event => this.setReducedMotion(Boolean(event.matches));
        if (this.mediaQuery.addEventListener) {
          this.mediaQuery.addEventListener('change', onChange);
          this.cleanup.push(() => this.mediaQuery.removeEventListener('change', onChange));
        } else if (this.mediaQuery.addListener) {
          this.mediaQuery.addListener(onChange);
          this.cleanup.push(() => this.mediaQuery.removeListener(onChange));
        }
      }

      const add = this.options.addEventListener || (global.addEventListener ? global.addEventListener.bind(global) : null);
      const remove = this.options.removeEventListener || (global.removeEventListener ? global.removeEventListener.bind(global) : null);
      if (add && remove) {
        const onResize = () => this.handleResize();
        add('resize', onResize, { passive: true });
        add('orientationchange', onResize, { passive: true });
        this.cleanup.push(() => remove('resize', onResize));
        this.cleanup.push(() => remove('orientationchange', onResize));
      }

      this.reset({ preserveTrigger: false, emit: false });
      if (this.reducedMotion) {
        this.showFinal({ reason: 'reduced-motion-connect' });
      } else {
        this.createObserver();
      }
      this.emit('connected');
      return this;
    }

    disconnect() {
      if (!this.connected) return this;
      this.cancelActive();
      if (this.observer && this.observer.disconnect) this.observer.disconnect();
      this.observer = null;
      for (const dispose of this.cleanup.splice(0)) {
        try { dispose(); } catch (_) {}
      }
      this.connected = false;
      return this;
    }

    destroy() {
      this.disconnect();
      this.destroyed = true;
      this.targets = [];
      this.root = null;
      return this;
    }

    createObserver() {
      if (this.reducedMotion || this.triggered) return;
      const Observer = this.options.IntersectionObserver || global.IntersectionObserver;
      if (typeof Observer !== 'function') {
        this.trigger('observer-unavailable');
        return;
      }
      this.observer = new Observer(entries => {
        for (const entry of entries) {
          if (entry.isIntersecting && entry.intersectionRatio >= this.options.threshold) {
            this.trigger('viewport-entry');
            if (this.options.once && this.observer) this.observer.disconnect();
            break;
          }
        }
      }, { threshold: [this.options.threshold] });
      this.observer.observe(this.root);
    }

    schedule(callback, delay, token) {
      const id = this.setTimer(() => {
        this.timeoutIds.delete(id);
        if (token === this.runToken && !this.destroyed) callback();
      }, delay);
      this.timeoutIds.add(id);
      return id;
    }

    cancelActive() {
      this.runToken += 1;
      for (const id of this.animationFrameIds) this.cancelFrame(id);
      for (const id of this.timeoutIds) this.clearTimer(id);
      this.animationFrameIds.clear();
      this.timeoutIds.clear();
      this.running = false;
    }

    write(target, text) {
      target.element.textContent = String(text);
    }

    reset(options) {
      const settings = { preserveTrigger: true, emit: true, ...(options || {}) };
      this.cancelActive();
      for (const target of this.targets) {
        if (target.type === 'numeric') this.write(target, target.formatter(target.from));
        else this.write(target, target.values[0]);
      }
      if (!settings.preserveTrigger) this.triggered = false;
      this.complete = false;
      this.assertNodeIdentity();
      if (settings.emit) this.emit('reset');
      return this;
    }

    replay() {
      if (!this.connected || this.destroyed) return this;
      this.reset({ preserveTrigger: true, emit: false });
      this.triggered = true;
      if (this.reducedMotion) this.showFinal({ reason: 'reduced-motion-replay' });
      else this.start('programmatic-replay');
      return this;
    }

    trigger(reason) {
      if (!this.connected || this.destroyed) return this;
      if (this.options.once && this.triggered) return this;
      this.triggered = true;
      if (this.reducedMotion) this.showFinal({ reason: reason || 'reduced-motion-trigger' });
      else this.start(reason || 'trigger');
      return this;
    }

    start(reason) {
      if (!this.connected || this.destroyed) return this;
      this.cancelActive();
      this.running = true;
      this.complete = false;
      const token = this.runToken;
      let completionAt = 0;

      for (const target of this.targets) {
        if (target.type === 'numeric') {
          completionAt = Math.max(completionAt, target.delay + target.duration);
          this.schedule(() => this.animateNumeric(target, token), target.delay, token);
        } else {
          completionAt = Math.max(completionAt, target.delay + ((target.values.length - 1) * target.stepMs));
          target.values.forEach((value, index) => {
            this.schedule(() => this.write(target, value), target.delay + (index * target.stepMs), token);
          });
        }
      }

      this.schedule(() => {
        this.applyFinalValues();
        this.running = false;
        this.complete = true;
        this.assertNodeIdentity();
        this.emit('complete', reason || 'start');
      }, completionAt + Math.max(0, Number(this.options.completionPaddingMs) || 0), token);
      this.emit('start', reason || 'start');
      return this;
    }

    animateNumeric(target, token) {
      const startedAt = this.now();
      const duration = target.duration;
      if (duration <= 0) {
        this.write(target, target.formatter(target.to));
        return;
      }
      const frame = now => {
        if (token !== this.runToken || this.destroyed) return;
        const progress = clamp((now - startedAt) / duration, 0, 1);
        const eased = clamp(target.easing(progress), 0, 1);
        const value = Math.round(target.from + ((target.to - target.from) * eased));
        this.write(target, target.formatter(value));
        if (progress < 1) {
          const id = this.requestFrame(nextNow => {
            this.animationFrameIds.delete(id);
            frame(nextNow);
          });
          this.animationFrameIds.add(id);
        } else {
          this.write(target, target.formatter(target.to));
        }
      };
      frame(this.now());
    }

    applyFinalValues() {
      for (const target of this.targets) {
        if (target.type === 'numeric') this.write(target, target.formatter(target.to));
        else this.write(target, target.finalText);
      }
    }

    showFinal(options) {
      if (!this.connected || this.destroyed) return this;
      this.cancelActive();
      this.applyFinalValues();
      this.triggered = true;
      this.running = false;
      this.complete = true;
      this.assertNodeIdentity();
      this.emit('complete', (options && options.reason) || 'final-state');
      return this;
    }

    setReducedMotion(value) {
      this.reducedMotion = Boolean(value);
      if (this.reducedMotion) {
        this.showFinal({ reason: 'reduced-motion-change' });
      } else if (!this.complete) {
        this.reset({ preserveTrigger: false });
        this.createObserver();
      } else {
        this.emit('reduced-motion-disabled');
      }
      return this;
    }

    handleResize() {
      if (!this.connected || this.destroyed) return;
      this.assertNodeIdentity();
      this.emit('resize-preserved');
    }

    assertNodeIdentity() {
      const stable = this.targets.every((target, index) => target.element === this.initialNodeIdentities[index]);
      if (!stable) throw new Error('Target node identity changed.');
      return true;
    }

    snapshot() {
      return {
        connected: this.connected,
        destroyed: this.destroyed,
        triggered: this.triggered,
        running: this.running,
        complete: this.complete,
        reducedMotion: this.reducedMotion,
        values: this.targets.map(target => ({
          id: target.id,
          type: target.type,
          text: String(target.element.textContent)
        })),
        nodeIdentityStable: this.assertNodeIdentity()
      };
    }

    getState() {
      return JSON.parse(JSON.stringify(this.lastState || this.snapshot()));
    }

    emit(phase, reason) {
      this.lastState = { ...this.snapshot(), phase, reason: reason || null };
      if (this.root && typeof this.root.dispatchEvent === 'function' && typeof global.CustomEvent === 'function') {
        this.root.dispatchEvent(new global.CustomEvent(this.options.eventName, { detail: this.getState() }));
      }
      if (typeof this.options.onChange === 'function') this.options.onChange(this.getState());
    }
  }

  function createStatisticsCounterCore(options) {
    return new StatisticsCounterCore(options);
  }

  const api = Object.freeze({
    StatisticsCounterCore,
    createStatisticsCounterCore,
    easeOutCubic,
    defaults: DEFAULTS
  });

  if (typeof module !== 'undefined' && module.exports) module.exports = api;
  global.StatisticsCounterCore = api;
})(typeof window !== 'undefined' ? window : globalThis);
