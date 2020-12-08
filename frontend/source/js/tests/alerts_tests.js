/* global QUnit document */

QUnit.module('alerts');

QUnit.test('sets tabindex=-1 and focuses itself when attached', (assert) => {
  const alerts = document.createElement('alerts-widget');
  alerts.focus = () => {
    assert.equal(alerts.getAttribute('tabindex'), '-1');
  };
  alerts.attachedCallback();
});

QUnit.test('emits alertswidgetready event', (assert) => {
  const done = assert.async();

  const fixture = document.getElementById('qunit-fixture');
  const div = document.createElement('div');

  div.addEventListener('alertswidgetready', () => {
    fixture.removeChild(div);
    assert.ok(true, 'alertswidgetready received');
    done();
  });

  div.innerHTML = '<alerts-widget>hi</alerts-widget>';

  fixture.appendChild(div);
});
