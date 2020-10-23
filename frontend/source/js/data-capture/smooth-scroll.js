/* global $, window */

/**
 * This script alters the behavior of in-page linking to smoothly
 * scroll the user's browser. It preserves sequential focus navigation
 * to ensure that keyboard users aren't stranded.
 *
 * Implementation notes
 * --------------------
 *
 * We use `history.replaceState()` to remember the current scroll
 * position of the page, so that we can restore it when the user
 * presses their browser's back and forward buttons.
 *
 * When the user clicks on an in-page link, however, we want to use
 * `location.hash` to set the new URL instead of `history.pushState()`
 * for a few reasons:
 *
 * * Using `location.hash` will invoke the sequential focus
 *   navigation behavior of browsers, which keeps things
 *   nice and accessible for keyboard users.
 *
 * * Using `history.pushState()` doesn't invoke `:target`
 *   CSS selectors, at the time of this writing, which is
 *   unfortunate (for more details, see
 *   https://bugs.webkit.org/show_bug.cgi?id=83490).
 *
 * However, we still want to store the current scroll
 * offset for the new history entry, so to do that we'll
 * wait for the `hashchange` event to fire and then use
 * `history.replaceState()`.
 */

// This is the amount of time, in milliseconds, that we'll take to
// scroll the page from its current position to a new position.
const DEFAULT_SCROLL_MS = 500;

// This determines whether we have enough functionality in the browser to
// support smooth scrolling.
export const IS_SUPPORTED = window.history && window.history.replaceState;

function buildPageState(object) {
  return Object.assign({}, window.history.state || {}, object);
}

function rememberCurrentScrollPosition(window) {
  window.history.replaceState(buildPageState({
    pageYOffset: window.pageYOffset,
  }), '');
}

function changeHash(window, hash, cb) {
  const currId = window.location.hash.slice(1);
  const newId = hash.slice(1);

  if (currId !== newId) {
    $(window).one('hashchange', cb);
  }
  window.location.hash = hash;
}

function smoothScroll(window, scrollTop, scrollMs, cb) {
  // WebKit uses `<body>` for keeping track of scrolling, while
  // Firefox and IE use `<html>`, so we need to animate both.

  const $els = $('html, body', window.document);
  let callbacksLeft = $els.length;

  $els.stop().animate({
    scrollTop,
  }, scrollMs, () => {
    // This callback is going to be called multiple times because
    // we're animating on multiple elements, but we only want the
    // code to execute once--hence our use of `callbacksLeft`.

    if (--callbacksLeft === 0) {
      if (cb) {
        cb();
      }
    }
  });
}

/**
 * Generate or retrieve an integer uniquely identifying this particular
 * page visit. The number will be the same if the user navigates back
 * to this page in the future.
 * */
export function getOrCreateVisitId(window) {
  const VISIT_ID_COUNTER = 'smoothScrollLatestVisitId';
  const VISIT_ID = 'smoothScrollVisitId';

  if (window.history.state && VISIT_ID in window.history.state) {
    return window.history.state[VISIT_ID];
  }

  const storage = window.sessionStorage;
  let latestVisitId = parseInt(storage[VISIT_ID_COUNTER], 10);

  if (isNaN(latestVisitId)) { /* eslint-disable-line no-restricted-globals */
    latestVisitId = 0;
  }

  storage[VISIT_ID_COUNTER] = ++latestVisitId;

  window.history.replaceState(buildPageState({
    [VISIT_ID]: latestVisitId,
  }), '');

  return latestVisitId;
}

function onPageReady(window, cb) {
  const doc = window.document;

  if (doc.readyState === 'interactive' || doc.readyState === 'complete') {
    cb();
  } else {
    window.addEventListener('DOMContentLoaded', cb, false);
  }
}

function smoothlyScrollToLocationHash(window, scrollMs) {
  onPageReady(window, () => {
    const id = window.location.hash.slice(1);
    const scrollTarget = window.document.getElementById(id);

    if (!scrollTarget) {
      return;
    }

    smoothScroll(window, $(scrollTarget).offset().top, scrollMs);
  });
}

/**
 * Some modern browsers support the scroll restoration API, which lets
 * us have full control over how the web page scrolls, eliminating
 * flicker caused by our code and the browser trying to "fight over"
 * the current scroll position.
 *
 * However, this also means we have to take care of some desirable
 * auto-scroll features that the browser normally takes care of for us,
 * such as auto-scrolling to the last known scroll position when the
 * user reloads or navigates back to our page from somewhere else.
 * */
export function activateManualScrollRestoration(window, scrollMs) {
  const doc = window.document;
  const storage = window.sessionStorage;
  const scrollKey = () => `visit_${getOrCreateVisitId(window)}_scrollTop`;
  const scrollTop = parseInt(storage[scrollKey()], 10);

  window.history.scrollRestoration = 'manual';

  if (isNaN(scrollTop)) { /* eslint-disable-line no-restricted-globals */
    smoothlyScrollToLocationHash(window, scrollMs);
  } else {
    onPageReady(window, () => {
      doc.documentElement.scrollTop = scrollTop;
      doc.body.scrollTop = scrollTop;
    });
  }

  window.addEventListener('beforeunload', () => {
    // We can't store the position in window.history.state here because
    // this will make some browsers flicker the URL in the address bar.
    storage[scrollKey()] = doc.documentElement.scrollTop
                           || doc.body.scrollTop;
  }, false);

  return window;
}

export function activate(window, options = {}) {
  const scrollMs = options.scrollMs || DEFAULT_SCROLL_MS;
  const onScroll = options.onScroll || (() => {});

  $('html', window.document).on('click', 'a[href^="#"]', (e) => {
    const scrollId = $(e.target).attr('href').slice(1);
    const scrollTarget = window.document.getElementById(scrollId);

    if (scrollTarget) {
      e.preventDefault();
      rememberCurrentScrollPosition(window);
      smoothScroll(window, $(scrollTarget).offset().top, scrollMs, () => {
        changeHash(window, `#${scrollId}`, () => {
          rememberCurrentScrollPosition(window);
          onScroll();
        });
      });
    }
  });

  window.addEventListener('popstate', (e) => {
    if (e.state && 'pageYOffset' in e.state) {
      smoothScroll(window, e.state.pageYOffset, scrollMs, onScroll);
    }
  }, false);

  // https://developers.google.com/web/updates/2015/09/history-api-scroll-restoration
  if ('scrollRestoration' in window.history) {
    activateManualScrollRestoration(window, scrollMs);
  }
}

if (IS_SUPPORTED) {
  activate(window);
}
