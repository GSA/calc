/* eslint-env browser */
/* global QUnit document */

import * as sinon from 'sinon';

import * as validation from '../data-capture/form-validation';

QUnit.module('form-validation');

class FakeForm {
  constructor() {
    Object.assign(this, {
      checkValidity: sinon.stub(),
      submit: sinon.stub(),
    });
  }
}

class FakeWindow {
  constructor(options = {}) {
    Object.assign(this, {
      history: {
        state: options.state || null,
        replaceState(state) {
          this.state = state;
        },
      },
      location: {
        hash: '',
      },
      document: {
        body: { scrollTop: 0 },
        documentElement: { scrollTop: 0 },
        readyState: options.readyState || 'loading',
        getElementById() { return null; },
        getElementsByClassName: sinon.stub(),
        querySelectorAll: sinon.stub(),
        querySelector: sinon.stub(),
        createElement(el) {
          return document.createElement(el);
        }
      },
      sessionStorage: options.sessionStorage || {},
      listeners: {},
    });
  }

  addEventListener(type, cb) {
    if (type in this.listeners) {
      throw new Error('only one listener per type expected');
    }
    this.listeners[type] = cb;
  }
}

function makeInputSet(isDate = true, hasErrorMsg = false) {
  const INVALID_MESSAGE_CLASS = 'form--invalid__message';
  const groupedFieldset = document.createElement('fieldset');
  const input1 = document.createElement('input');
  input1.classList.add('usa-input-inline');
  const input2 = document.createElement('input');
  input2.classList.add('usa-input-inline');
  const legend = document.createElement('legend');
  legend.innerText = 'I am legend';
  let subgroup = document.createElement('div');

  if (isDate) {
    subgroup = document.createElement('uswds-date');
  }

  if (hasErrorMsg) {
    const errorMsg = document.createElement('p');
    errorMsg.className = INVALID_MESSAGE_CLASS;
    errorMsg.innerText = 'DOES NOT COMPUTE';
    groupedFieldset.appendChild(errorMsg);
  }

  subgroup.appendChild(input1);
  subgroup.appendChild(input2);
  groupedFieldset.appendChild(legend);
  groupedFieldset.appendChild(subgroup);

  return {
    groupedFieldset,
    subgroup,
    input1,
    input2
  };
}

function makeInput(hasErrorMsg = false) {
  const INVALID_MESSAGE_CLASS = 'form--invalid__message';
  const fieldset = document.createElement('fieldset');
  const input = document.createElement('input');
  const label = document.createElement('label');
  label.innerText = 'Label me like one of your French girls';

  if (hasErrorMsg) {
    const errorMsg = document.createElement('p');
    errorMsg.className = INVALID_MESSAGE_CLASS;
    errorMsg.innerText = 'DOES NOT COMPUTE';
    fieldset.appendChild(errorMsg);
  }

  fieldset.appendChild(label);
  fieldset.appendChild(input);

  return { fieldset, input };
}

QUnit.test('getCustomMessage works', (assert) => {
  const ERROR_MESSAGES = {
    valueMissing: 'Please fill out this required field.',
  };

  const invalidValue = {
    typeMismatch: false,
    valueMissing: true,
  };

  const validInput = {
    typeMismatch: false,
    valueMissing: false,
  };

  assert.equal(validation.getCustomMessage('text', invalidValue), ERROR_MESSAGES.valueMissing);
  assert.equal(validation.getCustomMessage('text', validInput), undefined);
});

QUnit.test('findParentNode works', (assert) => {
  // simple inputs
  const singleFieldParent = document.createElement('fieldset');
  const singleField = document.createElement('input');

  singleFieldParent.appendChild(singleField);

  // compound inputs
  const { groupedFieldset, input1 } = makeInputSet();

  // inputs not wrapped in `fieldset`
  const faultyInputBody = document.createElement('body');
  const faultyInputParent = document.createElement('div');
  const faultyInput = document.createElement('input');
  faultyInputParent.appendChild(faultyInput);
  faultyInputBody.appendChild(faultyInputParent);

  assert.equal(validation.findParentNode(singleField), singleFieldParent);
  assert.equal(validation.findParentNode(input1), groupedFieldset);
  assert.equal(validation.findParentNode(faultyInput), null);
});

QUnit.test('toggleErrorMsg creates errors on single fields', (assert) => {
  const win = new FakeWindow();
  const INVALID_PARENT_CLASS = 'fieldset__form--invalid';
  const { fieldset } = makeInput();
  const parent = fieldset;

  const options = {
    showErrorMsg: true,
    message: "I am an empty input",
    parent,
  };
  validation.toggleErrorMsg(win, options);
  assert.ok(parent.classList.contains(INVALID_PARENT_CLASS));
  // This means the error message has been successfully appended to the DOM
  assert.ok(parent.firstChild.classList.contains('form--invalid__message'));
});

QUnit.test('toggleErrorMsg creates errors on grouped fields', (assert) => {
  const win = new FakeWindow();
  const INVALID_PARENT_CLASS = 'fieldset__form--invalid';
  const { groupedFieldset } = makeInputSet();
  const parent = groupedFieldset;
  const options = {
    showErrorMsg: true,
    message: "I am an empty input",
    parent,
  };

  validation.toggleErrorMsg(win, options);
  assert.ok(parent.classList.contains(INVALID_PARENT_CLASS));
  // This means the error message has been successfully appended to the DOM
  assert.ok(parent.firstChild.classList.contains('form--invalid__message'));
});

QUnit.test('toggleErrorMsg removes errors on single fields', (assert) => {
  const win = new FakeWindow();
  const hasErrorMsg = true;
  const { fieldset } = makeInput(hasErrorMsg);
  const parent = fieldset;
  const options = {
    showErrorMsg: false,
    message: null,
    parent,
  };

  validation.toggleErrorMsg(win, options);

  // Error class & div have been removed
  assert.equal(parent.classList.length, 0);
  assert.equal(parent.firstChild.tagName, 'LABEL');
  assert.ok(!parent.firstChild.classList.contains('form--invalid__message'));
});

QUnit.test('toggleErrorMsg removes errors on grouped fields', (assert) => {
  const win = new FakeWindow();
  const hasErrorMsg = true;
  const { groupedFieldset } = makeInputSet(hasErrorMsg);
  const parent = groupedFieldset;
  const options = {
    showErrorMsg: false,
    message: null,
    parent,
  };

  validation.toggleErrorMsg(win, options);

  // Error class & div have been removed
  assert.equal(parent.classList.length, 0);
  assert.equal(parent.firstChild.tagName, 'LEGEND');
  assert.ok(!parent.firstChild.classList.contains('form--invalid__message'));
});

QUnit.test('domContentLoaded submits the form when valid', (assert) => {
  const win = new FakeWindow();
  validation.window = win;

  const fakeForm = new FakeForm();

  const fakeSubmitButton = {
    addEventListener: (eventType, fn) => {
      fn();
    },
  };

  const { input } = makeInput();
  const { subgroup } = makeInputSet();

  win.document.getElementsByClassName.withArgs('form--contract_details').returns([fakeForm]);
  win.document.querySelectorAll.withArgs('input, select, textarea').returns([input]);
  win.document.querySelectorAll.withArgs('uswds-date').returns([subgroup]);
  win.document.querySelector.withArgs('.form--contract_details .submit-group button[type="submit"]').returns(fakeSubmitButton);

  fakeForm.checkValidity.returns(true);

  const result = validation.domContentLoaded(win); // eslint-disable-line no-unused-vars
  assert.ok(fakeForm.submit.called);
});

QUnit.test('domContentLoaded does not submit the form when invalid', (assert) => {
  const win = new FakeWindow();

  const fakeForm = new FakeForm();

  const fakeSubmitButton = {
    addEventListener: (eventType, fn) => {
      fn();
    },
  };

  const { input } = makeInput();
  const { subgroup } = makeInputSet();

  win.document.getElementsByClassName.withArgs('form--contract_details').returns([fakeForm]);
  win.document.querySelectorAll.withArgs('input, select, textarea').returns([input]);
  win.document.querySelectorAll.withArgs('uswds-date').returns([subgroup]);
  win.document.querySelector.withArgs('.submit-group button[type="submit"]').returns(fakeSubmitButton);

  fakeForm.checkValidity.returns(false);

  const result = validation.domContentLoaded(win); // eslint-disable-line no-unused-vars
  assert.ok(fakeForm.submit.notCalled);
});

QUnit.test('parseInputs works', (assert) => {
  const { subgroup, input1, input2 } = makeInputSet();
  const inputs = [input1, input2, document.createElement('input'), document.createElement('select'), document.createElement('textarea')];
  const groupedInputs = [subgroup];
  const result = validation.parseInputs(inputs, groupedInputs);
  assert.equal(result.singleInputs.length, 3);
  assert.equal(result.combinedInputs.length, 1);
});
