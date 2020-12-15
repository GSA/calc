/* global window, document */

import dispatchBubbly from './custom-event';

/**
 * AlertsWidget represents an <alerts-widget> web component.
 *
 * This component is useful for wrapping alerts that should be
 * telegraphed to screen-reader users in particular, as it is
 * focused when attached to the document tree, which causes screen
 * readers to announce the content of the widget immediately.
 */

class AlertsWidget extends window.HTMLElement {
  attachedCallback() {
    this.setAttribute('tabindex', '-1');
    this.focus();
    dispatchBubbly(this, 'alertswidgetready');
  }
}

AlertsWidget.prototype.SOURCE_FILENAME = __filename;

document.registerElement('alerts-widget', {
  prototype: AlertsWidget.prototype,
});
