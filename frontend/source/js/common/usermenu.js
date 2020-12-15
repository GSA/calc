// @ts-check
/* global document */


/**
 * Determines if `targetEl` is a descendant of the given `parentEl`.
 *
 * @param { HTMLElement|Element } parentEl the parent element
 * @param { HTMLElement|EventTarget|Element|null } targetEl the element in question
 * @returns { Boolean } `true` if `targetEl` is a descendant of `parentEl`.
 */
function isDescendantOf(parentEl, targetEl) {
  if (!targetEl || parentEl === targetEl) { return true; }

  let result = false;
  for (let index = 0; index < parentEl.children.length; index++) {
    const element = parentEl.children[index];
    result = result || isDescendantOf(element, targetEl);
  }

  return result;
}

/**
 * Sets the menu to an open or closed state based on `isOpen`.
 *
 * @param {Boolean} isOpen
 */
const toggleMenu = (isOpen) => {
  const menu = document.querySelector('#usermenu');
  const trigger = document.querySelector('#usermenu .usermenu-trigger');
  const openLabel = 'Show user menu';
  const closeLabel = 'Close user menu';

  if (!menu || !trigger) { return; }

  if (isOpen) {
    menu.classList.add('is-open');
  } else {
    menu.classList.remove('is-open');
  }

  trigger.setAttribute('aria-expanded', isOpen.toString());
  trigger.setAttribute('aria-label', isOpen ? closeLabel : openLabel);
};

function enableUsermenu() {
  const menu = document.querySelector('#usermenu');
  const trigger = document.querySelector('#usermenu .usermenu-trigger');
  const { body } = document;

  if (!menu || !trigger) { return; }

  trigger.setAttribute('aria-haspopup', true.toString());

  // start with the menu in the closed state
  toggleMenu(false);

  trigger.addEventListener('click', (e) => {
    e.preventDefault();
    const isOpen = menu.classList.contains('is-open');
    toggleMenu(!isOpen);
  });

  body.addEventListener('click', (e) => {
    if (!isDescendantOf(menu, e.target)) {
      toggleMenu(false);
    }
  });
}

document.addEventListener('DOMContentLoaded', enableUsermenu);
