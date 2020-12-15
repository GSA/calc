// @ts-check
/* eslint-env browser */

import { parse as urlParse } from "url";

/**
 * This is DAP's weird exported Google Analytics function, documented
 * at:
 *
 *     https://github.com/digital-analytics-program/gov-wide-code
 *
 * If DAP wasn't included at the top of the page, however, we'll just no-op
 * so that code which calls it still works, allowing DAP to be an optional
 * dependency.
 */
export function gas(...args) {
  const origGas = window['gas'];
  if (typeof origGas === 'function') {
    return origGas.apply(this, args);
  }
  return undefined;
}

/**
 * This is just a wrapper around Google Analytics' ga() function, which
 * should be included inline at the top of the page. If it wasn't included
 * at the top of the page, however, we'll just no-op
 * so that code which calls it still works, allowing GA to be an optional
 * dependency.
 */
export function ga(...args) {
  const origGa = window['ga'];
  if (typeof origGa === 'function') {
    return origGa.apply(this, args);
  }
  return undefined;
}

/**
 * Track a "virtual pageview" using Google Analytics. Typically
 * used in single-page apps and such. For more details, see:
 * 
 *   https://developers.google.com/analytics/devguides/collection/analyticsjs/pages
 *
 * @param {string} [url] The URL of the page to track, e.g. '/boop'.
 *   Defaults to the current page's URL, including the current
 *   search query.
 */
export function trackVirtualPageview(url) {
  ga('set', 'page', url || location.pathname + location.search); /* eslint-disable-line no-restricted-globals */
  ga('send', 'pageview');
  gas('send', 'pageview', url);
}


/**
 * Track a custom event. For more details, see:
 * 
 *   https://developers.google.com/analytics/devguides/collection/analyticsjs/events
 *
 * @param {string} category The event category; typically the object that
 *   was interacted with, e.g. 'download-graph'.
 * @param {string} action The type of interaction, e.g. 'click'.
 * @param {string} [label] Optional label for the event, useful for
 *   categorization.
 */
export function trackEvent(category, action, label) {
  ga('send', 'event', category, action, label);
  gas('send', 'event', category, action, label);
}

/**
 * This is a list of local URL prefixes that, when the target of
 * a link, imply that following the link will download
 * something to the user's system (e.g. a CSV file or Excel
 * spreadsheet).
 */
const LOCAL_DOWNLOAD_URLS = [
  '/api/',
  '/static/',
];

/**
 * If the given element is an "interesting" link, tracks it in GA.
 * Otherwise, this function does nothing.
 * 
 * By "interesting" we mean either a link that points to an external
 * site, or a link that will trigger a local download.
 * 
 * @param {any} el The element that might be an interesting link.
 */
function trackInterestingLink(el) {
  if (!(el instanceof HTMLAnchorElement)) {
    return;
  }

  // The 'host' and 'hostname' properties on IE11 are
  // unreliable, so we'll parse the URL manually.
  //
  // For more details, see:
  // https://github.com/18F/calc/pull/2007#discussion_r195593715
  const { pathname, host, hostname } = urlParse(el.href);

  if (!(pathname && host && hostname)) {
    return;
  }

  const isExternal = host !== window.location.host;

  if (isExternal) {
    // Note that the format of this event corresponds to
    // how DAP tracks outbound links. This is intentional, as it
    // means that anyone who wants to e.g. track statistics about
    // outbound links across all federal properties can do so,
    // and statistics from CALC will be included.
    trackEvent('Outbound', hostname, pathname);
  } else {
    const isLocalDownload = LOCAL_DOWNLOAD_URLS.some(
      url => pathname.indexOf(url) === 0
    );

    if (isLocalDownload) {
      trackEvent('Local Download', pathname, el.href);
    }
  }
}

/**
 * Auto-track all interesting link clicks made on the current page.
 */
export function autoTrackInterestingLinks() {
  document.documentElement.addEventListener('click', (e) => {
    trackInterestingLink(e.target);
  }, true);
}

/**
 * Track an exception. For more details, see:
 * 
 *   https://developers.google.com/analytics/devguides/collection/analyticsjs/exceptions
 * 
 * @param {string} description - A description of the exception.
 * @param {boolean?} isFatal - true if the exception was fatal.
 */
export function trackException(description, isFatal) {
  const fieldsObject = {
    exDescription: description,
    exFatal: isFatal || false
  };
  ga('send', 'exception', fieldsObject);
  gas('send', 'exception', fieldsObject);
}
