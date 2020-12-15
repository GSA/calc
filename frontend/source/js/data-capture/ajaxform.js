/* global jQuery, document, window */

import * as supports from './feature-detection';

import { trackVirtualPageview } from '../common/ga';

import dispatchBubbly from './custom-event';

const $ = jQuery;

const MISC_ERROR = 'Sorry, we’re having trouble. '
                   + 'Please try again later or refresh your browser.';

class Delegate {
  constructor(window) {
    this.window = window;
  }

  redirect(url) {
    // Some browsers will actually cache the state of our page, including
    // its DOM and JS, when the user navigates away from it, so that if/when
    // the user navigates back, the cached version is shown.
    //
    // In the case of ajaxform, this ultimately means that the user could
    // be shown the page in a state that we never expected it to be in, so
    // we'll use the 'pageshow' event, which is triggered in such situations,
    // to reload the page if this ever happens.
    //
    // For more details, see: http://stackoverflow.com/a/13123626

    this.window.onpageshow = (e) => {
      if (e.persisted) {
        this.window.location.reload();
      }
    };
    this.window.location = url;
  }

  alert(msg) {
    // TODO: Be more user-friendly here.
    this.window.alert(msg);
  }
}

let delegate = new Delegate(window);

exports.setDelegate = (newDelegate) => {
  delegate = newDelegate;
  return delegate;
};

exports.MISC_ERROR = MISC_ERROR;

/**
 * AjaxForm represents a <form is="ajax-form"> web component, which submits
 * a form via XMLHttpRequest (aka ajax) when the requisite browser
 * capabilities exist. If a browser doesn't support the prerequisites for
 * form submission via ajax, or if JS is disabled entirely, the form falls
 * back to a standard form.
 *
 * Note that when the form data is submitted via ajax, it is submitted
 * to the same URL, but with the `X-Requested-With: XMLHttpRequest`
 * header. This header should be detected on the server-side; if it's
 * set, the server is expected to respond with a JSON object containing
 * one of the following keys and values:
 *
 *   * `form_html`, containing a string value representing the HTML of a
 *     new <form is="ajax-form"> to replace the current form with. This is
 *     generally presented when there were server-side validation issues
 *     with the form.
 *
 *   * `redirect_url`, containing a string value representing the URL to
 *     redirect the user's browser to.
 */

class AjaxForm extends window.HTMLFormElement {
  attachedCallback() {
    this.isDegraded = !supports.formData()
                      || supports.isForciblyDegraded(this);
    if (!this.isDegraded) {
      $(this).on('submit', this._onUpgradedSubmit.bind(this));
    }
    dispatchBubbly(this, 'ajaxformready');
  }

  populateFormData(formData) {
    // IE11 doesn't support FormData.prototype.delete(), so we need to
    // manually construct the FormData ourselves (we used to have
    // the browser construct it for us, and then replace the file).
    for (let i = 0; i < this.elements.length; i++) {
      const el = this.elements[i];

      if (el.isUpgraded) {
        formData.append(el.name, el.upgradedValue);
      } else if (el.type === 'file') {
        for (let j = 0; j < el.files.length; j++) {
          formData.append(el.name, el.files[j]);
        }
      } else if (el.type === 'submit') {
        // This logic is used to support multiple submit buttons.
        // However, it's assumed that the "default" submit button, which
        // is triggered in browsers by being the first in the DOM tree,
        // has no 'name' value associated with it.
        if (document.activeElement === el) {
          formData.append(el.name, el.value);
        }
      } else if (el.type === 'radio' || el.type === 'checkbox') {
        // only append the radio or checkbox value if its `checked` property
        // is true
        if (el.checked) {
          formData.append(el.name, el.value);
        }
      } else {
        formData.append(el.name, el.value);
      }
    }

    return formData;
  }

  _replaceWithNewForm(html) {
    const newForm = $(html)[0];

    // Here we're assuming for analytics purposes that the
    // baseline (non-Ajax) version of this form would have resulted in
    // the user being sent to the page defined by the `action` attribute
    // of the form we're now loading. So we'll simulate that in GA.
    trackVirtualPageview($(newForm).attr('action'));

    // Replace the form and bind it.
    $(this).replaceWith(newForm);

    // Animate the new form so the user notices it.
    // TODO: Consider using a CSS class w/ a transition or animation instead.
    $(newForm).hide().fadeIn();
  }

  _onUpgradedSubmit(e) {
    e.preventDefault();

    const formData = new window.FormData();

    this.populateFormData(formData);

    const req = $.ajax(this.action, {
      processData: false,
      contentType: false,
      data: formData,
      method: this.method,
    });

    $(this).addClass('submit-in-progress');

    req.done((data) => {
      if (data.form_html) {
        this._replaceWithNewForm(data.form_html);
      } else if (data.redirect_url) {
        delegate.redirect(data.redirect_url);
      } else {
        delegate.alert(MISC_ERROR);
        $(this).removeClass('submit-in-progress');
      }
    });

    req.fail(() => {
      delegate.alert(MISC_ERROR);
      $(this).removeClass('submit-in-progress');
    });
  }
}

AjaxForm.prototype.SOURCE_FILENAME = __filename;

document.registerElement('ajax-form', {
  extends: 'form',
  prototype: AjaxForm.prototype,
});

exports.AjaxForm = AjaxForm;
exports.Delegate = Delegate;
