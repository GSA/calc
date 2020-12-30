/* global document, window */

/**
 * @license
 *
 * The following polyfill is based off the code at:
 *
 * https://developer.mozilla.org/en-US/docs/Web/API/CustomEvent/CustomEvent#Polyfill
 *
 * The polyfill is by Mozilla Contributors and licensed under CC-BY-SA 2.5:
 *
 * https://creativecommons.org/licenses/by-sa/2.5/
 */

if (typeof window.CustomEvent !== 'function') {
  const CustomEvent = (event, originalParams) => {
    const params = Object.assign({
      bubbles: false,
      cancelable: false,
      detail: undefined,
    }, originalParams || {});

    const evt = document.createEvent('CustomEvent');
    evt.initCustomEvent(event, params.bubbles, params.cancelable,
      params.detail);
    return evt;
  };

  CustomEvent.prototype = window.Event.prototype;
  window.CustomEvent = CustomEvent;
}

export default function dispatchBubbly(el, eventType, params) {
  el.dispatchEvent(new window.CustomEvent(eventType, Object.assign({
    bubbles: true,
  }, params || {})));
}
