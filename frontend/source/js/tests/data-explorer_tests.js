/* eslint-disable no-unused-vars */
/* global QUnit document $ */
import { appendHighlightedTerm } from '../data-explorer/autocomplete';

QUnit.module('data-explorer');

QUnit.test('appendHighlightedTerm() prevents stored XSS', (assert) => {
  assert.equal(
    appendHighlightedTerm(
      $('<span></span>'),
      'Project Manager of <script>alert("DOOM")</script>',
      'proj manager',
    ).html(),
    '<b>Proj</b>ect <b>Manager</b> of &lt;script&gt;alert("DOOM")&lt;/script&gt;',
  );
});

QUnit.test('appendHighlightedTerm() works', (assert) => {
  assert.equal(
    appendHighlightedTerm(
      $('<span></span>'),
      'superduperman',
      'super'
    ).html(),
    '<b>super</b>duperman'
  );

  assert.equal(
    appendHighlightedTerm(
      $('<span></span>'),
      'superduperman',
      'uper'
    ).html(),
    's<b>uper</b>d<b>uper</b>man'
  );

  // test to make sure it doesn't blow up on special-character-only search term
  assert.equal(
    appendHighlightedTerm(
      $('<span></span>'),
      'superduperman',
      '{{{'
    ).html(),
    'superduperman'
  );
});
