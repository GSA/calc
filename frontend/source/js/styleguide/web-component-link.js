/* global window, document */

class WebComponentLink extends window.HTMLAnchorElement {
  attachedCallback() {
    const tag = this.getAttribute('data-tag');
    const extendsClass = this.getAttribute('data-extends');
    let el;

    if (extendsClass) {
      el = document.createElement(tag, {
        is: extendsClass,
      });
    } else {
      el = document.createElement(tag);
    }

    const proto = Object.getPrototypeOf(el);

    if (!proto.SOURCE_FILENAME) {
      window.alert(
        `prototype for web component ${this.textContent} `
        + 'has no SOURCE_FILENAME property!',
      );
    }
    this.setAttribute('href', this.href + proto.SOURCE_FILENAME);
  }
}

// This is the critical piece of metadata that will tell
// WebComponentLink where a web component's source code
// is located. It needs to be defined on the prototype of
// every web component that's pointed at by a
// WebComponentLink, or else a JS alert will be raised.
WebComponentLink.prototype.SOURCE_FILENAME = __filename;

document.registerElement('web-component-link', {
  extends: 'a',
  prototype: WebComponentLink.prototype,
});
