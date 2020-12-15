/* global jQuery, document */

const $ = jQuery;

$(document).ready(() => {
  const editBtn = $('[data-edit-btn]');
  const contractDetails = $('[data-contract-details]');
  const editContractDetails = $('[data-edit-contract-details]');

  const requiredElements = [editBtn, contractDetails, editContractDetails];

  const hasAll = requiredElements.every($el => $el.length);
  const hasAny = requiredElements.some($el => $el.length);

  if (hasAll) {
    editBtn.click((e) => {
      contractDetails.slideUp();
      editContractDetails.slideDown();
      $('[data-edit-text]').each((_, el) => {
        $(el).text($(el).attr('data-edit-text'));
      });
      e.preventDefault();
    });
  } else if (hasAny) {
    throw new Error(
      'Warning! Couldn\'t find edit button and/or related elements, '
      + 'falling back to baseline behavior.',
    );
  }
});
