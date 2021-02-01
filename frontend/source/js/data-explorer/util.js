/* eslint-disable no-unused-vars */
/* global event */

import * as querystring from 'querystring';
import classNames from 'classnames';
import { format } from 'd3-format';

export const formatCommas = format(',');
export const formatPrice = format(',.0f');
export const formatPriceWithCents = format(',.02f');
export const formatFriendlyPrice = (price) => {
  if (Math.floor(price) === price) {
    return formatPrice(price);
  }
  return formatPriceWithCents(price);
};
export const checkforisNaN = (price) => {
  let returnableValue = price;
  if (Number.isNaN(price)) {
    returnableValue = 0;
  } 
  return returnableValue;
};


export const getMedian = (arr) => {
  let resultMedian = 0;
  const mid = Math.floor(arr.length / 2); 
  const nums = [...arr].sort((a, b) => a - b);
  resultMedian = arr.length % 2 !== 0 ? nums[mid] : (nums[mid - 1] + nums[mid]) / 2;
  return resultMedian;
};

const KEY_ENTER = 13;
const KEY_SPACE = 32;

export function handleEnter(cb) {
  return (event) => {
    if (event.keyCode === KEY_ENTER) {
      event.preventDefault();
      cb(event);
    }
  };
}

export function handleEnterOrSpace(cb) {
  return (event) => {
    if (event.keyCode === KEY_ENTER || event.keyCode === KEY_SPACE) {
      event.preventDefault();
      cb(event);
    }
  };
}

export function autobind(self, names) {
  const target = self;

  names.forEach((name) => {
    target[name] = target[name].bind(target);
  });
}

export function templatize(str, undef) {
  const undefFunc = () => undef;
  return d => str.replace(/{(\w+)}/g, (_, key) => d[key] || undefFunc.call(d, key));
}

export function parsePrice(value, defaultValue = 0) {
  let floatValue = parseFloat(value);

  if (isNaN(floatValue) || floatValue < 0) { /* eslint-disable-line no-restricted-globals */
    floatValue = defaultValue;
  }

  return floatValue;
}

export function filterActive(isActive, otherClasses = '') {
  return classNames(isActive ? 'filter_active' : '', otherClasses);
}

export function getLastCommaSeparatedTerm(term) {
  const pieces = term.split(/\s*,\s*/);
  return pieces[pieces.length - 1];
}

export function stripTrailingComma(str) {
  // Removes trailing comma and whitespace from given string
  return str.replace(/,\s*$/, '');
}

export function parseQueryString(str) {
  const qsObj = querystring.parse(str);

  // querystring.parse will create array values if a querystring param name
  // is repeated. We'll just take the first value of any such array.
  Object.keys(qsObj).forEach((key) => {
    const val = qsObj[key];
    if (Array.isArray(val)) {
      qsObj[key] = val[0]; /* eslint-disable-line prefer-destructuring */
    }
  });

  return qsObj;
}
