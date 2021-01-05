/* global QUnit document */

QUnit.module('uswds-date');

function makeDate() {
  const date = document.createElement('uswds-date');
  const input1 = document.createElement('input');
  const input2 = document.createElement('input');

  date.appendChild(input1);
  date.appendChild(input2);

  return { date, input1, input2 };
}

QUnit.test('input focus changed on "/"', (assert) => {
  const { date, input1, input2 } = makeDate();
  let defaultPrevented = false;

  input2.focus = () => {
    assert.ok(defaultPrevented);
  };

  date.handleKeyDown({
    keyCode: 191,
    target: input1,
    preventDefault: () => { defaultPrevented = true; },
  });
});

QUnit.test('input focus not changed when on last input', (assert) => {
  const { date, input1, input2 } = makeDate();
  let defaultPrevented = false;

  input1.focus = () => {
    throw new Error('I should not be called!');
  };

  date.handleKeyDown({
    keyCode: 191,
    target: input2,
    preventDefault: () => { defaultPrevented = true; },
  });

  assert.ok(!defaultPrevented);
});
