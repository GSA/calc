/* global window, document */

const KEY_DASH = 189;
const KEY_PERIOD = 190;
const KEY_SLASH = 191;

class UswdsDate extends window.HTMLElement {
  _getNextInput(currentInput) {
    const inputs = this.querySelectorAll('input');
    let useNext = false;

    for (let i = 0; i < inputs.length; i++) {
      if (useNext) {
        return inputs[i];
      } if (inputs[i] === currentInput) {
        useNext = true;
      }
    }

    return null;
  }

  handleKeyDown(e) {
    if (e.keyCode === KEY_DASH || e.keyCode === KEY_PERIOD
        || e.keyCode === KEY_SLASH) {
      const nextInput = this._getNextInput(e.target);

      if (nextInput) {
        e.preventDefault();
        nextInput.focus();
      }
    }
  }

  createdCallback() {
    this.addEventListener('keydown', this.handleKeyDown.bind(this), true);
  }
}

UswdsDate.prototype.SOURCE_FILENAME = __filename;

document.registerElement('uswds-date', {
  prototype: UswdsDate.prototype,
});

module.exports = UswdsDate;
