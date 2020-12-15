/* global window, document */

import * as supports from './feature-detection';

import { trackEvent } from '../common/ga';

import dispatchBubbly from './custom-event';

const KEY_SPACE = 32;
const KEY_ENTER = 13;

/**
 * ExpandableArea represents a <expandable-area> web component.
 */

class ExpandableArea extends window.HTMLElement {
  attachedCallback() {
    if ('isUpgraded' in this) {
      // We've already been attached.
      return;
    }

    // Note that this will always be undefined on IE6-8 because
    // `firstElementChild` wasn't added until IE9. But that's ok, it
    // just means we won't progressively enhance on those browsers.
    this.expander = this.firstElementChild;

    this.isUpgraded = Boolean(this.expander
                              && !supports.isForciblyDegraded(this));

    if (this.isUpgraded) {
      this.expander.setAttribute('aria-expanded', 'false');
      this.expander.setAttribute('role', 'button');
      this.expander.setAttribute('tabindex', '0');
      this.expander.onclick = this.toggle.bind(this);
      this.expander.onkeyup = (e) => {
        if (e.keyCode === KEY_SPACE || e.keyCode === KEY_ENTER) {
          this.toggle();
        }
      };
      dispatchBubbly(this, 'expandableareaready');
    }
  }

  toggle() {
    if (!this.isUpgraded) {
      return;
    }

    const newVal = this.expander.getAttribute('aria-expanded') === 'true'
      ? 'false' : 'true';
    this.expander.setAttribute('aria-expanded', newVal);
    trackEvent('expandable area',
      newVal === 'true' ? 'expand' : 'collapse',
      this.expander.textContent);
  }
}

ExpandableArea.prototype.SOURCE_FILENAME = __filename;

document.registerElement('expandable-area', {
  prototype: ExpandableArea.prototype,
});

module.exports = ExpandableArea;
