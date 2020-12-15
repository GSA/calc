/* global QUnit document */

QUnit.module('expandable-area');

QUnit.test('is not upgraded when empty', (assert) => {
  const ca = document.createElement('expandable-area');
  ca.attachedCallback();
  assert.strictEqual(ca.isUpgraded, false);
});

function makeArea() {
  const ca = document.createElement('expandable-area');
  const h1 = document.createElement('h1');
  ca.appendChild(h1);
  ca.attachedCallback();

  return { ca, h1 };
}

QUnit.test('is upgraded when containing at least one element', (assert) => {
  const { ca } = makeArea();
  assert.strictEqual(ca.isUpgraded, true);
});

QUnit.test('adds accessibility markup when upgraded', (assert) => {
  const { h1 } = makeArea();
  assert.equal(h1.getAttribute('aria-expanded'), 'false');
  assert.equal(h1.getAttribute('role'), 'button');
  assert.equal(h1.getAttribute('tabindex'), '0');
});

QUnit.test('toggle() flips aria-expanded value', (assert) => {
  const { ca, h1 } = makeArea();
  ca.toggle();
  assert.equal(h1.getAttribute('aria-expanded'), 'true');
  ca.toggle();
  assert.equal(h1.getAttribute('aria-expanded'), 'false');
});

QUnit.test('toggles on click', (assert) => {
  const { h1 } = makeArea();
  h1.onclick();
  assert.equal(h1.getAttribute('aria-expanded'), 'true');
});

QUnit.test('toggles on space', (assert) => {
  const { h1 } = makeArea();
  h1.onkeyup({ keyCode: 32 });
  assert.equal(h1.getAttribute('aria-expanded'), 'true');
});

QUnit.test('toggles on enter', (assert) => {
  const { h1 } = makeArea();
  h1.onkeyup({ keyCode: 13 });
  assert.equal(h1.getAttribute('aria-expanded'), 'true');
});

QUnit.test('does not toggle on other keys', (assert) => {
  const { h1 } = makeArea();
  for (let i = 0; i < 128; i++) {
    if (i !== 13 && i !== 32) {
      h1.onkeyup({ keyCode: i });
      assert.equal(h1.getAttribute('aria-expanded'), 'false',
        `does not toggle on keyCode == ${i}`);
    }
  }
});

QUnit.test('emits expandableareaready event', (assert) => {
  const done = assert.async();

  const fixture = document.getElementById('qunit-fixture');
  const div = document.createElement('div');

  div.addEventListener('expandableareaready', () => {
    fixture.removeChild(div);
    assert.ok(true, 'expandableareaready received');
    done();
  });

  div.innerHTML = '<expandable-area><h1>hi</h1></expandable-area>';

  fixture.appendChild(div);
});
