/* eslint-disable */

var globalErrorCount = 0;

function showEnableSafeModeUI() {
  var el = document.getElementById('safe-mode-enable');

  if (el && el.hasAttribute('style')) {
    el.removeAttribute('style');
    el.focus();
    if (typeof ga === 'function') {
      ga('send', 'event', 'safe mode', 'show');
    }
  }
}

window.onerror = function(msg, url, lineNumber) {
  globalErrorCount++;

  // Enclose the following in a try/catch to avoid infinite recursion.
  try {
    showEnableSafeModeUI();
  } catch (e) {}
};

window.onload = function() {
  if (globalErrorCount) {
    showEnableSafeModeUI();
  }
};
