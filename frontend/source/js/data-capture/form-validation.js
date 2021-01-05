/* global window */
/* eslint-disable consistent-return, no-else-return */

/**
 * HTML5 form validation doesn't apply our styles. Documented here:
 * https://github.com/18F/calc/issues/2017
 * This implementation is inspired by
 * https://pageclip.co/blog/2018-02-20-you-should-use-html5-form-validation.html
 */

const INVALID_MESSAGE_CLASS = 'form--invalid__message';
const INVALID_PARENT_CLASS = 'fieldset__form--invalid';
const FIELD_PARENT_NODE = 'fieldset';
// We can expand this list as needed depending on which errors we need custom messaging for.
// See list of possible error properties in this table:
// https://developer.mozilla.org/en-US/docs/Learn/HTML/Forms/Form_validation#Constraint_validation_API_properties
const ERROR_MESSAGES = {
  valueMissing: 'Please fill out this required field.',
};

export function getCustomMessage(type, validity) {
  if (validity.typeMismatch) {
    return ERROR_MESSAGES[`${type}Mismatch`];
  } else {
    for (const invalidKey in ERROR_MESSAGES) { // eslint-disable-line no-restricted-syntax
      if (validity[invalidKey]) {
        return ERROR_MESSAGES[invalidKey];
      }
    }
  }
}

// Radio buttons, inputs and USWDS date fields have deep nesting structures.
// We need to find the `fieldset` that contains the input in question and
// set the error message on that, otherwise we end up with multiple messages.
// Because we're using django-uswds-forms, every form should be encapsulated
// in a fieldset automatically.
export function findParentNode(node) {
  // tagName is always uppercase
  if (node.parentNode.tagName !== FIELD_PARENT_NODE.toUpperCase() && node.parentNode.tagName !== 'BODY') {
    return findParentNode(node.parentNode);
  } else if (node.parentNode.tagName === 'BODY') {
    // just in case we try to run this on something not in a fieldset, prevent infinite loop
    return null;
  } else {
    return node.parentNode;
  }
}

export function documentCreateElement(window, type) {
  return window.document.createElement(type);
}

export function toggleErrorMsg(window, options) {
  if (options.parent) {
    // I'm tired of typing `options`
    const { parent } = options;
    const errorContainer = parent.querySelector(`.${INVALID_MESSAGE_CLASS}`)
      || documentCreateElement(window, 'p');
    // grouped inputs like radios have legends; single inputs just have labels
    const fieldsetLabel = parent.getElementsByTagName('legend')[0] || parent.getElementsByTagName('label')[0];

    if (options.showErrorMsg && options.message) {
      errorContainer.className = INVALID_MESSAGE_CLASS;
      errorContainer.textContent = options.message;
      parent.insertBefore(errorContainer, fieldsetLabel);
      parent.classList.add(INVALID_PARENT_CLASS);
    } else {
      parent.classList.remove(INVALID_PARENT_CLASS);
      errorContainer.remove();
    }
  }
}

export function checkInputs(window, inputs) {
  inputs.singleInputs.forEach((input) => {
    // prevent showing the HTML5 tooltip
    input.addEventListener('invalid', (e) => {
      e.preventDefault();
    });

    // Set a custom message if the input is invalid.
    // Note that this overrides HTML5's built-in checkValidity() function,
    // which is why it's within the forEach scope -- we don't want to override
    // the master form's checkValidity() call.
    function checkValidity() { // eslint-disable-line no-unused-vars
      const message = input.validity.valid
        ? null
        : getCustomMessage(input.type, input.validity);

      input.setCustomValidity(message || '');
    }

    toggleErrorMsg(window, {
      showErrorMsg: !input.checkValidity(),
      message: input.validationMessage,
      parent: findParentNode(input),
    }, input);
  });

  inputs.combinedInputs.forEach((inputSet) => {
    // This does for a group of sibling inputs what the above function does for singles.
    // The biggest difference is that we need to track per-group errors -- if one
    // sibling is invalid, the whole group is invalid.

    // These only change if one of the inputs returns invalid.
    let groupIsValid = true;
    let message = null;
    let parent;

    inputSet.forEach((input) => {
      // prevent showing the HTML5 tooltip
      input.addEventListener('invalid', (e) => {
        e.preventDefault();
      });

      // We only need the parent to show/hide the error message. Since all inputs
      // in a group have the same parent, don't bother setting this more than once.
      if (!parent) {
        parent = findParentNode(input);
      }

      // Set a custom message if the input is invalid.
      // Note that this overrides HTML5's built-in checkValidity() function,
      // which is why it's within the forEach scope -- we don't want to override
      // the master form's checkValidity() call.
      function checkValidity() { // eslint-disable-line no-unused-vars
        const validationMsg = input.validity.valid
          ? null
          : getCustomMessage(input.type, input.validity);

        input.setCustomValidity(validationMsg || '');
      }

      message = input.validationMessage;

      if (input.checkValidity() === false) {
        groupIsValid = false;
      }
    });

    toggleErrorMsg(window, {
      showErrorMsg: !groupIsValid,
      message,
      parent: parent || null,
    });
  });
}

export function getCombinedInputs(inputWrapper) {
  return inputWrapper.querySelectorAll('input');
}

export function parseInputs(inputs, groupedInputs) {
  let singleInputs;
  let combinedInputs;
  if (inputs) {
    singleInputs = Array.from(inputs).filter(input => input.type !== 'hidden' && !input.classList.contains('usa-input-inline'));
  }
  if (groupedInputs) {
    // Dates must be validated as a set of inputs, otherwise one valid date part
    // will remove the message for the whole thing even though the set is not valid
    // (i.e., having a year but no month or day will be invalid, but will have no error message)
    combinedInputs = Array.from(groupedInputs).map(uswdsDate => getCombinedInputs(uswdsDate));
  }
  return {
    combinedInputs,
    singleInputs,
  };
}

export function domContentLoaded(win) {
  const form = win.document.getElementsByClassName('form--contract_details')[0];
  const inputs = parseInputs(win.document.querySelectorAll('input, select, textarea'), win.document.querySelectorAll('uswds-date'));
  const submitButton = win.document.querySelector('.form--contract_details .submit-group button[type="submit"]');
  if (form && inputs && submitButton) {
    submitButton.addEventListener('click', () => {
      const isValid = form.checkValidity();
      if (isValid) {
        form.submit();
      } else {
        // if the form is invalid, loop through the elements to discover
        // which need invalid messages. Check each valid element to make sure
        // it doesn't have an error message displayed.
        checkInputs(win, inputs);
      }
    });
  }
}

window.addEventListener('DOMContentLoaded', () => domContentLoaded(window));
