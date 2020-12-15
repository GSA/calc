/* global $, window, document */

// Many of the following feature detectors are ultimately pulled from
// Modernizr. Its license can be found here:
//
// https://github.com/Modernizr/Modernizr/blob/master/LICENSE

module.exports = {
  dragAndDrop() {
    const div = document.createElement('div');
    return ('draggable' in div) || ('ondragstart' in div && 'ondrop' in div);
  },

  formData() {
    return 'FormData' in window;
  },

  dataTransfer() {
    // Browsers that support FileReader support DataTransfer too.
    return 'FileReader' in window;
  },

  // We'd like to make it possible to forcibly degrade components that have
  // a `data-force-degradation` attribute on them or one of their
  // ancestors. This makes it easier to test degraded functionality and
  // also allows us to (potentially) provide a "safe mode" that users
  // who are experiencing browser compatibility issues can opt into.

  isForciblyDegraded(el) {
    return !!$(el).closest('[data-force-degradation]').length;
  },
};
