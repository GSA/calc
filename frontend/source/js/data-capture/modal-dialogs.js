/* eslint-disable no-unused-vars */
/* global $, document, window */

import A11yDialog from 'a11y-dialog';

$(document).ready(() => {
  const dialogs = {};

  $('[data-a11y-dialog-show]').each((i, el) => {
    // Create an A11yDialog instance for each unique data-a11y-dialog-show
    // target
    const $el = $(el);
    const dialogId = $el.attr('data-a11y-dialog-show');
    const dialogEl = document.getElementById(dialogId);
    const mainEl = document.getElementById('main');

    if (dialogEl && mainEl && !dialogs[dialogId]) {
      dialogs[dialogId] = new A11yDialog(dialogEl, mainEl);

      // Hook up listeners to add/remove the 'no-scroll' class to the
      // document body on hide/show of the modal dialog
      dialogEl.addEventListener('dialog:show', () => {
        $('body').addClass('no-scroll');
      });

      dialogEl.addEventListener('dialog:hide', () => {
        $('body').removeClass('no-scroll');
      });

      $el.click(e => e.preventDefault());
    }
  });
});
