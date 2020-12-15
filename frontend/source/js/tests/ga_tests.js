/* eslint-env browser */
/* global QUnit */

import * as ga from '../common/ga';

function clearGa() {
  delete window.ga;
  delete window.gas;
}

QUnit.module('ga', {
  beforeEach: clearGa,
  afterEach: clearGa,
});

QUnit.test('ga does not throw when window.ga is undefined', (assert) => {
  ga.ga();
  assert.ok(true, 'calling ga() does not throw');
});

QUnit.test('ga calls window.ga when it is a function', (assert) => {
  window.ga = (...args) => {
    assert.deepEqual(args, [1, 2, 3]);
  };
  ga.ga(1, 2, 3);
});

QUnit.test('gas does not throw when window.gas is undefined', (assert) => {
  ga.gas();
  assert.ok(true, 'calling gas() does not throw');
});

QUnit.test('gas calls window.gas when it is a function', (assert) => {
  window.gas = (...args) => {
    assert.deepEqual(args, [1, 2, 3]);
  };
  ga.gas(1, 2, 3);
});

QUnit.test('trackVirtualPageview() works', (assert) => {
  const log = [];
  window.ga = (...args) => {
    log.push('ga', args);
  };
  window.gas = (...args) => {
    log.push('gas', args);
  };
  ga.trackVirtualPageview('/blah');
  assert.deepEqual(log, [
    "ga",
    [
      "set",
      "page",
      "/blah"
    ],
    "ga",
    [
      "send",
      "pageview"
    ],
    "gas",
    [
      "send",
      "pageview",
      "/blah"
    ]
  ]);
});

QUnit.test('trackEvent() does not throw', (assert) => {
  assert.expect(2);
  window.ga = window.gas = (...args) => {
    assert.deepEqual(args, [
      'send', 'event', 'funky-widget', 'click', 'someCategory'
    ]);
  };
  ga.trackEvent('funky-widget', 'click', 'someCategory');
});

QUnit.test('autoTrackInterestingLinks() works', (assert) => {
  const a = document.createElement('a');

  document.body.appendChild(a);
  a.addEventListener('click', e => e.preventDefault());

  function assertClickLogs(expectedLog, msg) {
    const log = [];
    window.ga = (...args) => {
      log.push(args);
    };

    // There's an easier way to synthesize this event, but
    // this is the only way that works on IE11.
    const event = document.createEvent("MouseEvent");
    event.initMouseEvent(
      'click', true, true, window,
      0, 0, 0, 0, 0, false, false, false, false, 1, null
    );

    a.dispatchEvent(event);
    assert.deepEqual(log, expectedLog, msg);
  }

  try {
    a.setAttribute('href', '/api/blorp');
    assertClickLogs([[
      "send",
      "event",
      "Local Download",
      "/api/blorp",
      `${location.origin}/api/blorp` /* eslint-disable-line no-restricted-globals */
    ]], "Local downloads are tracked");

    a.setAttribute('href', 'https://example.com/blah');
    assertClickLogs([[
      "send",
      "event",
      "Outbound",
      "example.com",
      `/blah`
    ]], "Outbound links are tracked");

    a.setAttribute('href', '/');
    assertClickLogs([], "Internal links are not tracked");
  } finally {
    document.body.removeChild(a);
  }
});
