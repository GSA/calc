/**
 * This module provides functionality for serializing/deserializing
 * Data Explorer search query parameters to/from strings in a
 * secure way. Ultimately, this allows the search query to be
 * represented in the current URL's querystring.
 */

import {
  EDU_LABELS,
  MIN_EXPERIENCE,
  MAX_EXPERIENCE,
  SITE_LABELS,
  BUSINESS_SIZE_LABELS,
  SIN_NUMBER,
  SECURITY_CLEARANCE_LABELS,
  CONTRACT_YEAR_LABELS,
  DEFAULT_CONTRACT_YEAR,
  DEFAULT_SORT,
  DEFAULT_QUERY_TYPE,
  QUERY_TYPE_LABELS,
  SORT_KEYS,
  MAX_QUERY_LENGTH,
  QUERY_BY_VENDOR,
  QUERY_BY_CONTRACT,
} from './constants';

import {
  scheduleLabels,
} from './schedule-metadata';

import {
  parsePrice,
} from './util';

const parseSort = (val) => {
  if (val) {
    let key = val;
    let descending = false;

    if (val.charAt(0) === '-') {
      key = val.substr(1);
      descending = true;
    }

    if (SORT_KEYS.indexOf(key) !== -1) {
      return { key, descending };
    }
  }

  return DEFAULT_SORT;
};

const coercedString = (val) => {
  if (val === undefined) {
    return '';
  }
  return String(val);
};

const coercedExperience = defaultVal => (val) => {
  const valInt = parseInt(val, 10);

  if (isNaN(valInt)) { /* eslint-disable-line no-restricted-globals */
    return defaultVal;
  }

  return Math.max(Math.min(valInt, MAX_EXPERIENCE), MIN_EXPERIENCE);
};

const stringInSet = (choices, defaultVal = '') => (val) => {
  if (val in choices) {
    return val;
  }

  return defaultVal;
};

const stringInArray = (choices, defaultVal = '') => (val) => {
  for (let i = 0; i < choices.length; i++) {
    if (choices[i] === val) {
      return val;
    }
  }
  return defaultVal;
};

export const serializers = {
  exclude: list => list.map(coercedString).join(','),
  education: list => list.map(coercedString).join(','),
  q: coercedString,
  'contract-year': coercedString,
  site: coercedString,
  business_size: coercedString,
  sinNumber: coercedString,
  securityClearance: coercedString,
  schedule: coercedString,
  min_experience: coercedString,
  max_experience: coercedString,
  'proposed-price': coercedString,
  sort: ({ key, descending }) => (descending ? '-' : '') + key,
  query_type: coercedString,
  query_by: coercedString,
};


export const deserializers = { 
  exclude: list => coercedString(list)
    .split(',')
    .map(x => parseInt(x, 10))
    .filter(x => !isNaN(x)), /* eslint-disable-line no-restricted-globals */
  education: list => coercedString(list)
    .split(',')
    .filter(x => x in EDU_LABELS),
  q: s => coercedString(s).slice(0, MAX_QUERY_LENGTH),
  'contract-year': stringInSet(CONTRACT_YEAR_LABELS, DEFAULT_CONTRACT_YEAR),
  site: stringInSet(SITE_LABELS),
  business_size: stringInSet(BUSINESS_SIZE_LABELS),
  sinNumber: stringInSet(SIN_NUMBER),
  securityClearance: stringInSet(SECURITY_CLEARANCE_LABELS),
  schedule: stringInSet(scheduleLabels),
  min_experience: coercedExperience(MIN_EXPERIENCE),
  max_experience: coercedExperience(MAX_EXPERIENCE),
  'proposed-price': parsePrice,
  sort: parseSort,
  query_type: stringInSet(QUERY_TYPE_LABELS, DEFAULT_QUERY_TYPE),
  query_by: stringInArray([QUERY_BY_VENDOR, QUERY_BY_CONTRACT]),
};

export const allFields = Object.keys(serializers);

export function getSerializedFields(state, fields, options = {}) {
  const result = {};
  fields.forEach((field) => {
    const val = serializers[field](state[field]);

    if (options.omitEmpty && !val.length) {
      return;
    }

    result[field] = val;
  });

  return result;
}

export function getChangedSerializedFields(oldState, newState, fields) {
  const result = {};

  fields.forEach((field) => {
    const oldVal = serializers[field](oldState[field]);
    const newVal = serializers[field](newState[field]);

    if (oldVal !== newVal) {
      result[field] = newVal;
    }
  });

  return result;
}
