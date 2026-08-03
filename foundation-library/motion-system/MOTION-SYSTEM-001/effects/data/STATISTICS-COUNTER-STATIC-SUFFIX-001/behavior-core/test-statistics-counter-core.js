'use strict';
const assert = require('node:assert/strict');
const { createStatisticsCounterCore } = require('./statistics-counter-core.js');

class FakeNode {
  constructor(text = '') { this.nodeType = 1; this.textContent = text; this.events = []; }
  dispatchEvent(event) { this.events.push(event); return true; }
}

class FakeRoot extends FakeNode {
  constructor() { super(''); this.map = new Map(); }
  add(selector, node) { this.map.set(selector, node); return node; }
  querySelector(selector) { return this.map.get(selector) || null; }
}

class Scheduler {
  constructor() { this.time = 0; this.nextId = 1; this.tasks = new Map(); }
  setTimeout(fn, delay) { const id = this.nextId++; this.tasks.set(id, { time: this.time + delay, fn, type: 'timeout' }); return id; }
  clearTimeout(id) { this.tasks.delete(id); }
  requestAnimationFrame(fn) { const id = this.nextId++; this.tasks.set(id, { time: this.time + 16, fn: () => fn(this.time), type: 'frame' }); return id; }
  cancelAnimationFrame(id) { this.tasks.delete(id); }
  runUntil(target) {
    while (true) {
      let selected = null;
      for (const [id, task] of this.tasks) {
        if (task.time <= target && (!selected || task.time < selected.task.time || (task.time === selected.task.time && id < selected.id))) selected = { id, task };
      }
      if (!selected) break;
      this.tasks.delete(selected.id);
      this.time = selected.task.time;
      selected.task.fn();
    }
    this.time = target;
  }
  runAll(limit = 10000) {
    let guard = 0;
    while (this.tasks.size) {
      if (++guard > limit) throw new Error('scheduler runaway');
      const nextTime = Math.min(...Array.from(this.tasks.values()).map(task => task.time));
      this.runUntil(nextTime);
    }
  }
}

class FakeObserver {
  constructor(callback) { this.callback = callback; this.disconnected = false; this.target = null; FakeObserver.instances.push(this); }
  observe(target) { this.target = target; }
  disconnect() { this.disconnected = true; }
  fire(ratio = 1) { this.callback([{ isIntersecting: true, intersectionRatio: ratio, target: this.target }]); }
}
FakeObserver.instances = [];

function build(reduced = false) {
  const root = new FakeRoot();
  const patients = root.add('#patients', new FakeNode('1000'));
  const plus = root.add('#plus', new FakeNode('+'));
  const years = root.add('#years', new FakeNode('28'));
  const pillars = root.add('#pillars', new FakeNode('Audición, Lenguaje y TDAH'));
  const portalSuffix = root.add('#portalSuffix', new FakeNode('/7'));
  const scheduler = new Scheduler();
  const listeners = new Map();
  const mediaListeners = new Set();
  const media = {
    matches: reduced,
    addEventListener: (_, fn) => mediaListeners.add(fn),
    removeEventListener: (_, fn) => mediaListeners.delete(fn)
  };
  const states = [];
  const core = createStatisticsCounterCore({
    root,
    targets: [
      { id: 'patients', element: patients, type: 'numeric', from: 0, to: 1000, delay: 0, duration: 1600 },
      { id: 'years', element: years, type: 'numeric', from: 0, to: 28, delay: 100, duration: 1250 },
      { id: 'pillars', element: pillars, type: 'sequence', values: ['Audición', 'Audición, Lenguaje', 'Audición, Lenguaje y TDAH'], delay: 200, stepMs: 205 },
      { id: 'portalSuffix', element: portalSuffix, type: 'sequence', values: ['', '/', '/7'], delay: 320, stepMs: 180 }
    ],
    IntersectionObserver: FakeObserver,
    matchMedia: () => media,
    now: () => scheduler.time,
    requestAnimationFrame: fn => scheduler.requestAnimationFrame(fn),
    cancelAnimationFrame: id => scheduler.cancelAnimationFrame(id),
    setTimeout: (fn, delay) => scheduler.setTimeout(fn, delay),
    clearTimeout: id => scheduler.clearTimeout(id),
    addEventListener: (name, fn) => listeners.set(name, fn),
    removeEventListener: name => listeners.delete(name),
    onChange: state => states.push(state)
  });
  core.connect();
  return { core, root, patients, plus, years, pillars, portalSuffix, scheduler, listeners, media, mediaListeners, states };
}

(function normalMotionAndStaticSuffix() {
  FakeObserver.instances.length = 0;
  const env = build(false);
  const plusIdentity = env.plus;
  assert.equal(env.patients.textContent, '0');
  assert.equal(env.plus.textContent, '+');
  FakeObserver.instances.at(-1).fire(0.4);
  const samples = [];
  for (let t = 0; t <= 1800; t += 50) {
    env.scheduler.runUntil(t);
    samples.push(Number(env.patients.textContent));
    assert.notEqual(env.patients.textContent, '');
    assert.strictEqual(env.plus, plusIdentity);
    assert.equal(env.plus.textContent, '+');
  }
  env.scheduler.runAll();
  assert.equal(env.patients.textContent, '1000');
  assert.equal(env.years.textContent, '28');
  assert.equal(env.pillars.textContent, 'Audición, Lenguaje y TDAH');
  assert.equal(env.portalSuffix.textContent, '/7');
  assert.ok(samples.every((value, index) => index === 0 || value >= samples[index - 1]));
  assert.equal(env.core.getState().complete, true);
  assert.equal(env.core.getState().nodeIdentityStable, true);
})();

(function reducedMotionImmediateFinal() {
  FakeObserver.instances.length = 0;
  const env = build(true);
  assert.equal(env.patients.textContent, '1000');
  assert.equal(env.years.textContent, '28');
  assert.equal(env.pillars.textContent, 'Audición, Lenguaje y TDAH');
  assert.equal(env.portalSuffix.textContent, '/7');
  assert.equal(env.core.getState().reducedMotion, true);
  assert.equal(env.core.getState().complete, true);
})();

(function oneShotReentryDoesNotRestart() {
  FakeObserver.instances.length = 0;
  const env = build(false);
  const observer = FakeObserver.instances.at(-1);
  observer.fire(0.4);
  env.scheduler.runAll();
  const token = env.core.runToken;
  env.core.trigger('reentry');
  assert.equal(env.core.runToken, token);
  assert.equal(env.patients.textContent, '1000');
  assert.equal(env.core.getState().complete, true);
})();

(function replayCancelsStaleCallbacks() {
  FakeObserver.instances.length = 0;
  const env = build(false);
  FakeObserver.instances.at(-1).fire(0.4);
  env.scheduler.runUntil(300);
  env.core.replay();
  const replayToken = env.core.runToken;
  env.scheduler.runAll();
  assert.equal(env.core.runToken, replayToken);
  assert.equal(env.patients.textContent, '1000');
  assert.equal(env.years.textContent, '28');
  assert.equal(env.portalSuffix.textContent, '/7');
  assert.equal(env.core.getState().complete, true);
})();

(function resizePreservesFinalStateAndDoesNotRestart() {
  FakeObserver.instances.length = 0;
  const env = build(false);
  FakeObserver.instances.at(-1).fire(0.4);
  env.scheduler.runAll();
  const token = env.core.runToken;
  env.listeners.get('resize')();
  assert.equal(env.core.runToken, token);
  assert.equal(env.patients.textContent, '1000');
  assert.equal(env.portalSuffix.textContent, '/7');
  assert.equal(env.core.getState().phase, 'resize-preserved');
})();

(function configurableAndSourceIndependent() {
  const root = new FakeRoot();
  const alpha = new FakeNode('9');
  const beta = new FakeNode('done');
  const scheduler = new Scheduler();
  const core = createStatisticsCounterCore({
    root,
    targets: [
      { id: 'alpha', element: alpha, type: 'numeric', from: 5, to: 9, duration: 64 },
      { id: 'beta', element: beta, type: 'sequence', values: ['a', 'b', 'done'], stepMs: 10 }
    ],
    IntersectionObserver: undefined,
    matchMedia: () => ({ matches: false }),
    now: () => scheduler.time,
    requestAnimationFrame: fn => scheduler.requestAnimationFrame(fn),
    cancelAnimationFrame: id => scheduler.cancelAnimationFrame(id),
    setTimeout: (fn, delay) => scheduler.setTimeout(fn, delay),
    clearTimeout: id => scheduler.clearTimeout(id)
  });
  core.connect();
  scheduler.runAll();
  assert.equal(alpha.textContent, '9');
  assert.equal(beta.textContent, 'done');
})();

(function destroyStopsMutation() {
  FakeObserver.instances.length = 0;
  const env = build(false);
  FakeObserver.instances.at(-1).fire(0.4);
  env.scheduler.runUntil(200);
  env.core.destroy();
  const value = env.patients.textContent;
  env.scheduler.runAll();
  assert.equal(env.patients.textContent, value);
  assert.equal(env.core.destroyed, true);
})();

console.log(JSON.stringify({
  status: 'PASS',
  tests: 7,
  assertions: 'normal,reduced-motion,one-shot-reentry,replay-cancellation,resize-preservation,source-independence,destroy-cancellation'
}, null, 2));
