/* eslint-disable no-unused-vars */
/* global QUnit $ test document window QUNIT_FIXTURE_DATA */

import { parse as urlParse } from 'url';

import * as sinon from 'sinon';

import * as ajaxform from '../data-capture/ajaxform';

import { UploadWidget } from '../data-capture/upload';

let server;
let $parentDiv;

QUnit.module('ajaxform', {
  beforeEach() {
    server = sinon.fakeServer.create();
  },
  afterEach() {
    server.restore();
    if ($parentDiv) {
      $parentDiv.remove();
      $parentDiv = null;
    }
  },
});

function createBlob(content) {
  // In a more modern engine with Blob support
  if (window.Blob) {
    return new window.Blob([content]);
  }

  throw new Error('Unable to determine how to create Blob');
}

function makeFormHtml(extraOptions) {
  const options = Object.assign({
    isDegraded: false,
    fooValue: 'bar',
    aRadioSelectedValue: '2',
    someCheckboxesValues: ['b', 'c'],
  }, extraOptions || {});

  const $form = $('<div></div>')
    .html(QUNIT_FIXTURE_DATA.AJAXFORM_TESTS_HTML);

  if (options.isDegraded) {
    $form.find('form').attr('data-force-degradation', '');
  }

  $form.find('input[name="foo"]').attr('value', options.fooValue);

  // Normally, we would want to set the DOM property `checked` to true
  // but since we are using this method to generate HTML, we need to use
  // the attribute `checked` (which sets the default state of the radio)
  $form.find(`input[name="a_radio"][value="${options.aRadioSelectedValue}"]`)
    .attr('checked', true);

  const checkboxValues = Array.isArray(options.someCheckboxesValues)
    ? options.someCheckboxesValues : [options.someCheckboxesValues];

  // Same as above for setting the `checked` attributes of the selected
  // checkbox values
  checkboxValues.forEach((val) => {
    $form.find(`input[name='some_checkboxes'][value=${val}]`)
      .attr('checked', true);
  });

  return $form.html();
}

function addForm(extraOptions, cb) {
  const div = $('<div></div>').appendTo('body').hide();

  $parentDiv = div;

  Promise.all([
    new Promise(resolve => div.one('uploadwidgetready', resolve)),
    new Promise(resolve => div.one('ajaxformready', resolve)),
  ]).then((results) => {
    cb({
      uploadinput: results[0].target.uploadInput,
      ajaxform: results[1].target,
      setFile(file) {
        this.uploadinput.upgradedValue = file;
      },
    });
  });

  div.html(makeFormHtml(extraOptions));
}

function formTest(name, options, originalCb) {
  let cb = originalCb;
  let extraOptions = options;

  if (!cb) {
    cb = extraOptions;
    extraOptions = undefined;
  }
  return QUnit.test(name, (assert) => {
    const done = assert.async();
    addForm(extraOptions, (s) => {
      cb(assert, s);
      done();
    });
  });
}

function advancedTest(name, extraOptions, cb) {
  // Our advanced tests embed an upload widget in them, which has a
  // superset of the features required for ajaxform, so we'll test
  // against that.
  if (!UploadWidget.HAS_BROWSER_SUPPORT) {
    return QUnit.skip(name, cb);
  }
  return formTest(name, extraOptions, cb);
}

class FakeFormData {
  constructor() {
    this.appended = [];
  }

  append(name, value) {
    this.appended.push([name, value]);
  }
}

formTest('degraded form has truthy .isDegraded', {
  isDegraded: true,
}, (assert, s) => {
  assert.ok(s.ajaxform.isDegraded);
});

formTest('degraded form does not cancel form submission', {
  isDegraded: true,
}, (assert, s) => {
  $(s.ajaxform).on('submit', (e) => {
    assert.ok(!e.isDefaultPrevented());
    e.preventDefault();
  });

  $(s.ajaxform).submit();
});

test('Delegate.redirect() works', (assert) => {
  const fakeWindow = {};
  const delegate = new ajaxform.Delegate(fakeWindow);
  let reloadCalled = false;

  delegate.redirect('http://boop');
  assert.equal(fakeWindow.location, 'http://boop');
  fakeWindow.location = { reload: () => { reloadCalled = true; } };
  fakeWindow.onpageshow({ persisted: true });
  assert.ok(reloadCalled);
});

test('Delegate.alert() works', (assert) => {
  const messages = [];
  const fakeWindow = { alert(msg) { messages.push(msg); } };
  const delegate = new ajaxform.Delegate(fakeWindow);

  delegate.alert('boop');
  assert.deepEqual(messages, ['boop']);
});

test('populateFormData() works w/ non-upgraded file inputs', (assert) => {
  const formData = ajaxform.AjaxForm.prototype.populateFormData.call({
    elements: [{
      type: 'file',
      name: 'boop',
      files: ['fakeFile'],
    }],
  }, new FakeFormData());

  assert.deepEqual(formData.appended, [['boop', 'fakeFile']]);
});

advancedTest('upgraded form has falsy .isDegraded', (assert, s) => {
  assert.ok(!s.ajaxform.isDegraded);
});

advancedTest('custom submit btn info only included when '
             + 'in active focus', (assert, s) => {
  $(s.ajaxform).on('submit', () => {
    const formData = server.requests[0].requestBody;

    // Ugh, only newer browsers support FormData.prototype.get().
    if (typeof formData.get === 'function') {
      assert.ok(formData.has('cancel'));
    } else {
      assert.ok(true);
    }
  });
  $parentDiv.show();
  $('button[name="cancel"]', s.ajaxform).focus();
  $(s.ajaxform).submit();
});

advancedTest('submit triggers ajax w/ form data', (assert, s) => {
  $(s.ajaxform).on('submit', (e) => {
    assert.ok(e.isDefaultPrevented());
    assert.equal(server.requests.length, 1);

    const req = server.requests[0];
    const formData = req.requestBody;

    assert.equal(req.method, 'POST');
    assert.equal(urlParse(req.url).path, '/post-stuff');

    // Ugh, only newer browsers support FormData.prototype.get().
    if (typeof formData.get === 'function') {
      assert.equal(formData.get('foo'), 'bar');
      assert.equal(formData.get('a_radio'), '2');
      assert.deepEqual(formData.getAll('some_checkboxes'), ['b', 'c']);
      assert.equal(formData.get('file').size, 'hello there'.length);
      assert.ok(!formData.has('cancel'));
    }
  });

  s.setFile(createBlob('hello there'));

  $(s.ajaxform).submit();
});

advancedTest('submitted XHR has X-Requested-With header', (assert, s) => {
  s.setFile(createBlob('hello there'));
  $(s.ajaxform).submit();

  const req = server.requests[0];
  assert.equal(req.requestHeaders['X-Requested-With'], 'XMLHttpRequest');
});

advancedTest('form_html replaces form & rebinds it', {
  fooValue: 'hello',
}, (assert, s) => {
  function getForm() {
    const $form = $('form', $parentDiv);
    assert.equal($form.length, 1);
    return $form[0];
  }

  const origForm = getForm();

  assert.equal($('input[name="foo"]', origForm).val(), 'hello');

  s.setFile(createBlob('blah'));
  $(origForm).submit();

  server.requests[0].respond(
    200,
    { 'Content-Type': 'application/json' },
    JSON.stringify({
      form_html: makeFormHtml({ fooValue: 'blargyblarg' }),
    }),
  );

  const newForm = getForm();

  assert.ok(newForm !== origForm);
  assert.equal($('input[name="foo"]', newForm).val(), 'blargyblarg');
});

advancedTest('redirect_url redirects browser', (assert, s) => {
  s.setFile(createBlob('blah'));
  $(s.ajaxform).submit();

  const delegate = ajaxform.setDelegate({ redirect: sinon.spy() });

  server.requests[0].respond(
    200,
    { 'Content-Type': 'application/json' },
    JSON.stringify({
      redirect_url: 'http://boop',
    }),
  );

  assert.ok(delegate.redirect.calledWith('http://boop'));
});

advancedTest('500 results in alert', (assert, s) => {
  s.setFile(createBlob('blah'));
  $(s.ajaxform).submit();

  const delegate = ajaxform.setDelegate({ alert: sinon.spy() });

  server.requests[0].respond(500);

  assert.ok(delegate.alert.calledWith(ajaxform.MISC_ERROR));
});

advancedTest('unrecognized 200 results in alert', (assert, s) => {
  s.setFile(createBlob('blah'));
  $(s.ajaxform).submit();

  const delegate = ajaxform.setDelegate({ alert: sinon.spy() });

  server.requests[0].respond(200);

  assert.ok(delegate.alert.calledWith(ajaxform.MISC_ERROR));
});
