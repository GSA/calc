/* global QUnit jQuery document test QUNIT_FIXTURE_DATA */

import * as sinon from 'sinon';

import { UploadWidget } from '../data-capture/upload';

function mockOriginalEvent(extras) {
  return Object.assign({
    preventDefault: () => {},
    stopPropagation: () => {},
  }, extras);
}

(function uploadTests(QUnit, $) {
  const UPLOAD_HTML = QUNIT_FIXTURE_DATA.UPLOAD_TESTS_HTML;

  let $parentDiv;
  let upload;
  let input;

  function makeWidget(isDegraded, cb, options = {}) {
    const div = document.createElement('div');

    $parentDiv = $(div);

    if (isDegraded) {
      div.setAttribute('data-force-degradation', '');
    }

    div.addEventListener('uploadwidgetready', (e) => {
      upload = $(e.target);
      input = upload.find('input');
      cb();
    });

    // On browsers with native support for custom elements, this
    // could synchronously upgrade the elements.
    div.innerHTML = UPLOAD_HTML;

    if (options.fakeInitialFilename) {
      $('upload-widget', div).attr('data-fake-initial-filename',
        options.fakeInitialFilename);
    }

    // This will cause the attached/connected callbacks (depending on
    // version of custom elements spec) to be triggered.
    document.body.appendChild(div);
  }

  function degradedTest(name, cb) {
    return QUnit.test(name, (assert) => {
      const done = assert.async();

      makeWidget(true, () => {
        cb(assert);
        done();
      });
    });
  }

  function advancedTest(name, cb, options = {}) {
    if (!UploadWidget.HAS_BROWSER_SUPPORT) {
      return QUnit.skip(name, cb);
    }
    return QUnit.test(name, (assert) => {
      const done = assert.async();

      makeWidget(false, () => {
        cb(assert);
        done();
      }, options);
    });
  }

  QUnit.module('upload', {
    afterEach() {
      if ($parentDiv) {
        $parentDiv.remove();
        $parentDiv = null;
      }
      upload = null;
      input = null;
    },
  });

  test('HAS_BROWSER_SUPPORT is a boolean', (assert) => {
    assert.equal(typeof UploadWidget.HAS_BROWSER_SUPPORT, 'boolean');
  });

  test('widget w/ non-ajaxform form is always degraded', (assert) => {
    const div = document.createElement('div');
    const done = assert.async();

    div.addEventListener('uploadwidgetready', (e) => {
      assert.ok(e.target.isDegraded);
      done();
    });

    div.innerHTML = '<form style="display: none"><upload-widget>'
                    + '<input type="file" is="upload-input">'
                    + '</upload-widget></form>';
    document.body.appendChild(div);
  });

  test('upload-input removes "required" attr on upgrade', (assert) => {
    upload = document.createElement('input', { is: 'upload-input' });
    upload.setAttribute('required', '');
    upload.upgrade();
    assert.ok(!upload.hasAttribute('required'));
  });

  test('upload-input calls setCustomValidity() if required', (assert) => {
    upload = document.createElement('input', { is: 'upload-input' });
    upload.setAttribute('required', '');
    upload.setCustomValidity = sinon.spy();
    upload.upgrade();
    assert.deepEqual(upload.setCustomValidity.args, [
      ['Please choose a file.'],
    ]);
    upload.upgradedValue = 'fakefile';
    assert.deepEqual(upload.setCustomValidity.args, [
      ['Please choose a file.'],
      [''],
    ]);
    assert.ok(upload.upgradedValue, 'fakefile');
  });

  test('upload-input works when setCustomValidity is undefined', (assert) => {
    upload = document.createElement('input', { is: 'upload-input' });
    upload.setAttribute('required', '');
    upload.setCustomValidity = undefined;
    upload.upgrade();
    upload.upgradedValue = 'fakefile';
    assert.ok(upload.upgradedValue, 'fakefile');
  });

  degradedTest('degraded upload has falsy .isUpgraded', (assert) => {
    assert.ok(!input[0].isUpgraded);
  });

  degradedTest('degraded upload sets attributes properly', (assert) => {
    assert.ok(!upload[0].hasAttribute('aria-live'));
  });

  advancedTest('advanced upload has truthy .isUpgraded', (assert) => {
    assert.ok(input[0].isUpgraded);
    assert.strictEqual(input[0].upgradedValue, null);
  });

  advancedTest('advanced upload sets aria-live', (assert) => {
    assert.equal(upload.attr('aria-live'), 'polite');
  });

  advancedTest('advanced upload sets fake filename if provided', (assert) => {
    assert.equal(upload.find('.upload-filename').text(), 'boop.csv');
  }, {
    fakeInitialFilename: 'boop.csv',
  });

  advancedTest('advanced upload does not set filename by default', (assert) => {
    assert.equal(upload.find('.upload-filename').text(), '');
  });

  advancedTest('advanced upload does not allow non-accepted file types', (assert) => {
    const badFakeFile = { name: 'boop', type: 'application/badtest' };
    const evt = jQuery.Event('drop', {
      originalEvent: mockOriginalEvent({ dataTransfer: { files: [badFakeFile] } }),
    });

    upload.trigger(evt);
    assert.strictEqual(input[0].upgradedValue, null);
    assert.ok(upload.find('.upload-error').length);
  });

  advancedTest('advanced upload allows accepted file types', (assert) => {
    const goodFileMime = { name: 'boop', type: 'application/test' };
    const mimeDropEvt = jQuery.Event('drop', {
      originalEvent: mockOriginalEvent({ dataTransfer: { files: [goodFileMime] } }),
    });

    upload.trigger(mimeDropEvt);
    assert.strictEqual(input[0].upgradedValue, goodFileMime);

    const goodFileExt = { name: 'boop.csv', type: 'whatever' };
    const extDropEvt = jQuery.Event('drop', {
      originalEvent: mockOriginalEvent({ dataTransfer: { files: [goodFileExt] } }),
    });
    upload.trigger(extDropEvt);
    assert.strictEqual(input[0].upgradedValue, goodFileExt);
  });

  advancedTest('advanced upload allows any file when "accept" not specified', (assert) => {
    input.attr('accept', null);
    const fakeFile = { name: 'boop' };
    const evt = jQuery.Event('drop', {
      originalEvent: mockOriginalEvent({ dataTransfer: { files: [fakeFile] } }),
    });
    upload.trigger(evt);
    assert.strictEqual(input[0].upgradedValue, fakeFile);
  });

  advancedTest('"changefile" event triggered on drop', (assert) => {
    const fakeFile = { name: 'boop', type: 'application/test' };
    const evt = jQuery.Event('drop', {
      originalEvent: mockOriginalEvent({ dataTransfer: { files: [fakeFile] } }),
    });

    upload.on('changefile', (e) => {
      assert.strictEqual(e.originalEvent.detail, fakeFile);
    });
    upload.trigger(evt);
  });

  advancedTest('input "change" evt w/o files does nothing', (assert) => {
    input.trigger('change');
    assert.strictEqual(input[0].upgradedValue, null);
  });

  advancedTest('changing .upgradedValue sets current file', (assert) => {
    const fakeFile = { name: 'foo.txt', type: 'application/test' };

    input.on('changefile', (e) => {
      assert.strictEqual(e.originalEvent.detail, fakeFile);
      assert.equal(upload.find('.upload-filename').text(), 'foo.txt');
    });

    input[0].upgradedValue = fakeFile;
  });

  advancedTest('dragenter/dragleave affect .dragged-over', (assert) => {
    assert.ok(!upload.hasClass('dragged-over'));

    const OUTER_EL = 'I am a fake outer element';
    const INNER_EL = 'I am a fake inner element';

    // Simulate user dragging over the outer element.
    upload.trigger(new $.Event('dragenter', { target: OUTER_EL }));
    assert.ok(upload.hasClass('dragged-over'));

    // Simulate user dragging over the inner element.
    upload.trigger(new $.Event('dragenter', { target: INNER_EL }));
    upload.trigger(new $.Event('dragleave', { target: OUTER_EL }));
    assert.ok(upload.hasClass('dragged-over'));

    // Simulate user dragging out of the inner element.
    upload.trigger(new $.Event('dragenter', { target: OUTER_EL }));
    upload.trigger(new $.Event('dragleave', { target: INNER_EL }));
    assert.ok(upload.hasClass('dragged-over'));

    // Simulate user dragging out of the outer element.
    upload.trigger(new $.Event('dragleave', { target: OUTER_EL }));
    assert.ok(!upload.hasClass('dragged-over'));
  });

  advancedTest('spurious dragenter events are ignored', (assert) => {
    const EL = 'I am a fake element';

    // Simulate user dragging over the element.
    upload.trigger(new $.Event('dragenter', { target: EL }));
    assert.ok(upload.hasClass('dragged-over'));

    // Simulate https://bugzilla.mozilla.org/show_bug.cgi?id=804036.
    upload.trigger(new $.Event('dragenter', { target: EL }));
    assert.ok(upload.hasClass('dragged-over'));

    // Simulate user dragging out of the element.
    upload.trigger(new $.Event('dragleave', { target: EL }));
    assert.ok(!upload.hasClass('dragged-over'));
  });
}(QUnit, jQuery));
