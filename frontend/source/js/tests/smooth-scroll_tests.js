/* eslint-disable no-unused-vars */
/* global $ QUnit document window */

import {
  IS_SUPPORTED,
  activate,
  activateManualScrollRestoration,
  getOrCreateVisitId,
} from '../data-capture/smooth-scroll';

QUnit.module('smooth-scroll');

function test(name, cb) {
  if (!IS_SUPPORTED) {
    return QUnit.skip(name, cb);
  }

  return QUnit.test(name, cb);
}

// Ugh, some browsers don't fire `onhashchange` within iframes, so
// we'll polyfill it.
function addHashChangePolyfill(window) {
  let oldHash = window.location.hash;

  window.setInterval(() => {
    const newHash = window.location.hash;

    if (newHash !== oldHash) {
      $(window).trigger('hashchange');
      oldHash = newHash;
    }
  }, 10);
}

class FakeWindow {
  constructor(options = {}) {
    Object.assign(this, {
      history: {
        state: options.state || null,
        replaceState(state) {
          this.state = state;
        },
      },
      location: {
        hash: '',
      },
      document: {
        body: { scrollTop: 0 },
        documentElement: { scrollTop: 0 },
        readyState: options.readyState || 'loading',
        getElementById() { return null; },
      },
      sessionStorage: options.sessionStorage || {},
      listeners: {},
    });
  }

  addEventListener(type, cb) {
    if (type in this.listeners) {
      throw new Error('only one listener per type expected');
    }
    this.listeners[type] = cb;
  }

  getScrollTop() {
    if (this.document.body.scrollTop
        !== this.document.documentElement.scrollTop) {
      // These need to be the same because some browsers use
      // the <body>'s scrollTop to control scrolling, while others use
      // the <html>'s scrollTop.
      throw new Error('scrollTop of <body> and <html> are not the same');
    }
    return this.document.body.scrollTop;
  }
}

test('getOrCreateVisitId() returns existing visit id', (assert) => {
  const win = new FakeWindow({ state: { smoothScrollVisitId: 5 } });
  assert.equal(getOrCreateVisitId(win), 5);
});

test('getOrCreateVisitId() creates new visit id', (assert) => {
  const win = new FakeWindow();
  assert.equal(getOrCreateVisitId(win), 1);
  assert.equal(win.history.state.smoothScrollVisitId, 1);
});

test('getOrCreateVisitId() updates latest visit id counter', (assert) => {
  const win = new FakeWindow({
    sessionStorage: { smoothScrollLatestVisitId: '300' },
  });
  assert.equal(getOrCreateVisitId(win), 301);
  assert.equal(win.sessionStorage.smoothScrollLatestVisitId, '301');
});

test('amsr sets history.scrollRestoration', (assert) => {
  const win = activateManualScrollRestoration(new FakeWindow());
  assert.equal(win.history.scrollRestoration, 'manual');
});

test('amsr remembers scrollTop on window unload', (assert) => {
  const win = activateManualScrollRestoration(new FakeWindow());
  win.document.body.scrollTop = 5;
  win.listeners.beforeunload();
  assert.equal(win.sessionStorage.visit_1_scrollTop, '5');
});

test('amsr scrolls to last scrollTop on DOMContentLoaded', (assert) => {
  const win = activateManualScrollRestoration(new FakeWindow({
    state: { smoothScrollVisitId: 201 },
    sessionStorage: { visit_201_scrollTop: '20' },
  }));
  assert.equal(win.getScrollTop(), 0);
  win.listeners.DOMContentLoaded();
  assert.equal(win.getScrollTop(), 20);
});

test('amsr scrolls to last scrollTop if readyState=interactive', (assert) => {
  const win = activateManualScrollRestoration(new FakeWindow({
    state: { smoothScrollVisitId: 201 },
    sessionStorage: { visit_201_scrollTop: '20' },
    readyState: 'interactive',
  }));
  assert.equal(win.getScrollTop(), 20);
});

test('amsr scrolls to last scrollTop if readyState=complete', (assert) => {
  const win = activateManualScrollRestoration(new FakeWindow({
    state: { smoothScrollVisitId: 201 },
    sessionStorage: { visit_201_scrollTop: '20' },
    readyState: 'complete',
  }));
  assert.equal(win.getScrollTop(), 20);
});

test('amsr does not set scrollTop if last value was corrupt', (assert) => {
  const win = activateManualScrollRestoration(new FakeWindow({
    state: { smoothScrollVisitId: 201 },
    sessionStorage: { visit_201_scrollTop: 'LOL' },
    readyState: 'complete',
  }));
  assert.equal(win.getScrollTop(), 0);
});

test('activate() works', (assert) => {
  const iframe = document.createElement('iframe');
  const getScrollTop = () => $('body', iframe.contentDocument).scrollTop()
    || $('html', iframe.contentDocument).scrollTop();

  $(iframe).appendTo('body').css({
    height: '50px',
    visibility: 'hidden',
  });

  iframe.contentDocument.open();
  iframe.contentDocument.write([
    '<a href="#foo">foo</a>',
    '<h1>hello</h1>',
    '<h2>there</h2>',
    '<h2 id="foo">foo</h1>',
  ].join('\n'));
  iframe.contentDocument.close();

  addHashChangePolyfill(iframe.contentWindow);

  const done = assert.async();
  const steps = (function* runSteps() {
    assert.equal(iframe.contentWindow.location.hash, '');
    assert.equal(getScrollTop(), 0);

    yield $('a', iframe.contentDocument).click();

    assert.equal(iframe.contentWindow.location.hash, '#foo');
    assert.ok(getScrollTop() !== 0);

    yield iframe.contentWindow.history.back();

    assert.equal(iframe.contentWindow.location.hash, '');
    assert.equal(getScrollTop(), 0);

    yield iframe.contentWindow.history.forward();

    assert.equal(iframe.contentWindow.location.hash, '#foo');
    assert.ok(getScrollTop() !== 0);

    $(iframe).remove();
    done();
  }());

  activate(iframe.contentWindow, {
    scrollMs: 50,
    onScroll: () => steps.next(),
  });

  steps.next();
});
