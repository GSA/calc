/* global $, window, document */
/* eslint-disable prefer-destructuring */


import * as supports from './feature-detection';

import dispatchBubbly from './custom-event';

const HAS_BROWSER_SUPPORT = supports.dragAndDrop() && supports.formData()
                            && supports.dataTransfer();

/**
 * UploadInput represents a <input is="upload-input" type="file"> web
 * component.
 *
 * Unlike a standard file input, it allows for the file to be set by
 * client code via the `upgradedValue` property. However, in order for the
 * input to be writable, client code must call its `upgrade()` method and
 * manually submit the `upgradedValue` to a server via ajax.
 */

export class UploadInput extends window.HTMLInputElement {
  createdCallback() {
    this.isUpgraded = false;
    this._upgradedValue = null;
  }

  attachedCallback() {
    if (this.getAttribute('type') !== 'file') {
      throw new Error('<input is="upload-input"> must have type "file".');
    }
    if (this.hasAttribute('multiple')) {
      throw new Error('<input is="upload-input"> does not currently '
                      + 'support the "multiple" attribute.');
    }
    dispatchBubbly(this, 'uploadinputready');
  }

  upgrade() {
    this.isUpgraded = true;
    $(this).on('change', () => {
      this.upgradedValue = this.files[0];
    });
    if (this.hasAttribute('required')) {
      // We don't want the browser to enforce the required attribute, because
      // if we programmatically set our file (e.g. via a drag-and-drop)
      // the browser will still think the file input is empty.

      this.removeAttribute('required');

      // Instead, we'll set our own custom validity manually, assuming the
      // user's browser supports HTML5 form validation.

      if (this.setCustomValidity) {
        this.setCustomValidity('Please choose a file.');
      }
    }
  }

  get upgradedValue() {
    return this._upgradedValue;
  }

  set upgradedValue(file) {
    if (!file) {
      return;
    }

    if (!this.isFileValid(file)) {
      dispatchBubbly(this, 'invalidfile');
      return;
    }

    this._upgradedValue = file;
    $(this).val('');

    if (this.setCustomValidity) {
      this.setCustomValidity('');
    }

    dispatchBubbly(this, 'changefile', {
      detail: file,
    });
  }

  isFileValid(file) {
    const accepts = $(this).attr('accept');
    if (!accepts || !accepts.length) {
      // nothing specified, so just return true
      return true;
    }
    const fileType = file.type.toLowerCase();
    const fileName = file.name.toLowerCase();
    const acceptsList = accepts.split(',').map(s => s.trim().toLowerCase());

    return acceptsList.some(extOrType => (
      (fileType === extOrType)
      || (fileName.lastIndexOf(extOrType, fileName.length - extOrType.length) !== -1)
    ));
  }
}

UploadInput.prototype.SOURCE_FILENAME = __filename;

document.registerElement('upload-input', {
  extends: 'input',
  prototype: UploadInput.prototype,
});

/**
 * UploadWidget represents a <upload-widget> web component, which provides
 * a large area for users to drag-and-drop files into. It also serves as a
 * sort of view into the state of a nested <input is="upload-input">, telling
 * the user the name of the current file to be uploaded, and reporting
 * errors (such as invalid file type) if necessary.
 *
 * An <upload-widget> must be nested within a <form is="ajax-form"> in order
 * to work properly, since supporting HTML5 drag-and-drop necessitates
 * submitting the dropped file via ajax.
 */

export class UploadWidget extends window.HTMLElement {
  static stopAndPrevent(event) {
    event.stopPropagation();
    event.preventDefault();
  }

  _checkForAjaxFormParent() {
    if (this.uploadInput.form
        && this.uploadInput.form.getAttribute('is') !== 'ajax-form') {
      if (window.console && window.console.log) {
        window.console.log(
          'Warning: <upload-widget> must have a '
          + '<form is="ajax-form"> parent in order to support '
          + 'drag-and-drop.',
        );
      }
      return false;
    }
    return true;
  }

  attachedCallback() {
    const $el = $(this);
    const $input = $('input', $el);

    if ($input.length !== 1 || $input.attr('is') !== 'upload-input') {
      throw new Error('<upload-widget> must contain exactly one '
                      + '<input is="upload-input">.');
    }

    this.uploadInput = $input[0];
    this.isDegraded = false;

    let dragCounter = 0;
    let lastDragEnterTarget = null;

    function setCurrentFilename(filename) {
      $('input', $el).nextAll().remove();

      const id = $('input', $el).attr('id');
      const current = $(
        '<div class="upload-current">'
        + '<div class="upload-filename"></div>'
        + '<div class="upload-changer">Not right? '
        + '<label>Choose a different file</label> or drag and drop here.'
        + '</div></div>',
      );
      $('label', current).attr('for', id);
      $('.upload-filename', current).text(filename);
      $el.append(current);
    }

    const finishInitialization = () => {
      if (this.uploadInput instanceof UploadInput) {
        if (!this.isDegraded) {
          this.uploadInput.upgrade();

          const fakeInitialFilename = $el.attr('data-fake-initial-filename');

          if (fakeInitialFilename) {
            setCurrentFilename(fakeInitialFilename);
          }
        }
        dispatchBubbly($el[0], 'uploadwidgetready');
      } else {
        $el.one('uploadinputready', finishInitialization);
      }
    };

    function showInvalidFileMessage() {
      $('input', $el).nextAll().remove();

      const id = $('input', $el).attr('id');
      const err = $(
        '<div class="upload-error">'
        + '<div class="upload-error-message">Sorry, that type of file is not allowed.</div>'
        + 'Please <label>choose a different file</label> or drag and drop one here.'
        + '</div></div>',
      );
      $('label', err).attr('for', id);
      $el.append(err);
    }

    if (!this._checkForAjaxFormParent() || !HAS_BROWSER_SUPPORT
        || supports.isForciblyDegraded(this)) {
      this.isDegraded = true;
      return finishInitialization();
    }

    $('label', $el)
      .after('<span aria-hidden="true"> or drag and drop here.</span>');

    // The content of the upload widget will change when the user chooses
    // a file, so let's make sure screen readers let users know about it.
    // Note that this is also used by CSS rules to determine whether or
    // not the widget has actually been upgraded by JS.
    $el.attr('aria-live', 'polite');

    $el.on('dragenter', (e) => {
      UploadWidget.stopAndPrevent(e);

      // Firefox spuriously fires multiple `dragenter` events, which
      // we need to work around by keeping track of the most recent
      // event target. For more information, see:
      //
      //   https://bugzilla.mozilla.org/show_bug.cgi?id=804036

      if (lastDragEnterTarget !== e.target) {
        dragCounter++;
        $el.addClass('dragged-over');
        lastDragEnterTarget = e.target;
      }
    });
    $el.on('dragleave', () => {
      lastDragEnterTarget = null;
      // http://stackoverflow.com/a/21002544/2422398
      if (--dragCounter === 0) {
        $el.removeClass('dragged-over');
      }
    });
    $el.on('dragover', UploadWidget.stopAndPrevent.bind(this));
    $el.on('drop', (e) => {
      UploadWidget.stopAndPrevent(e);
      $el.removeClass('dragged-over');
      dragCounter = 0;
      lastDragEnterTarget = null;

      this.uploadInput.upgradedValue = e.originalEvent.dataTransfer.files[0];
    });

    $input.on('invalidfile', showInvalidFileMessage);

    $input.on('changefile', (e) => {
      setCurrentFilename(e.originalEvent.detail.name);
    });

    return finishInitialization();
  }
}

UploadWidget.prototype.SOURCE_FILENAME = __filename;

UploadWidget.HAS_BROWSER_SUPPORT = HAS_BROWSER_SUPPORT;

document.registerElement('upload-widget', {
  prototype: UploadWidget.prototype,
});
