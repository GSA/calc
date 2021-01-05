export const EXCLUDE_ROW = 'EXCLUDE_ROW';
export const EXCLUDE_NONE = 'EXCLUDE_NONE';
export const SET_STATE = 'SET_STATE';
export const RESET_STATE = 'RESET_STATE';
export const START_RATES_REQUEST = 'START_RATES_REQUEST';
export const COMPLETE_RATES_REQUEST = 'COMPLETE_RATES_REQUEST';
export const INVALIDATE_RATES = 'INVALIDATE_RATES';
export const SET_SORT = 'SET_SORT';
export const SET_PROPOSED_PRICE = 'SET_PROPOSED_PRICE';
export const SET_EXPERIENCE = 'SET_EXPERIENCE';
export const TOGGLE_EDU_LEVEL = 'TOGGLE_EDU_LEVEL';
export const ADD_CAT_LEVEL = 'ADD_CAT_LEVEL';
export const ADD_SUB_CAT_LEVEL = 'ADD_SUB_CAT_LEVEL';
export const REMOVE_CAT_LEVEL = 'REMOVE_CAT_LEVEL';
export const REMOVE_SUB_CAT_LEVEL = 'REMOVE_SUB_CAT_LEVEL';
export const REMOVE_ALL_SUB_CAT_LEVELS = 'REMOVE_ALL_SUB_CAT_LEVELS';
export const SET_SCHEDULE = 'SET_SCHEDULE';
export const SET_CONTRACT_YEAR = 'SET_CONTRACT_YEAR';
export const SET_QUERY_TYPE = 'SET_QUERY_TYPE';
export const SET_SITE = 'SET_SITE';
export const SET_BUSINESS_SIZE = 'SET_BUSINESS_SIZE';
export const SET_QUERY = 'SET_QUERY';
export const SET_QUERY_BY = 'SET_QUERY_BY';
export const SET_SIN_NUMBER = 'SET_SIN_NUMBER';
export const SET_SECURITY_CLEARANCE = 'SET_SECURITY_CLEARANCE';

export function excludeRow(rowId) {
  return { type: EXCLUDE_ROW, rowId };
}

export function excludeNone() {
  return { type: EXCLUDE_NONE };
}

export function setState(value) {
  return { type: SET_STATE, value };
}

export function resetState() {
  return { type: RESET_STATE };
}

export function startRatesRequest() {
  return { type: START_RATES_REQUEST };
}

export function completeRatesRequest(error, data) {
  return {
    type: COMPLETE_RATES_REQUEST,
    error,
    data,
  };
}

export function invalidateRates() {
  return { type: INVALIDATE_RATES };
}

export function setSort({ key, descending }) {
  return {
    type: SET_SORT,
    key,
    descending,
  };
}

export function setProposedPrice(price) {
  return { type: SET_PROPOSED_PRICE, price };
}

export function setExperience(subtype, years) {
  return { type: SET_EXPERIENCE, subtype, years };
}

export function toggleEducationLevel(level) {
  return { type: TOGGLE_EDU_LEVEL, level };
}

export function addCatLevel(level) {
  return { type: ADD_CAT_LEVEL, level };
}

export function addSubCatLevel(level) {
  return { type: ADD_SUB_CAT_LEVEL, level };
}

export function removeCatLevel(level) {
  return { type: REMOVE_CAT_LEVEL, level };
}

export function removeSubCatLevel(level) {
  return { type: REMOVE_SUB_CAT_LEVEL, level };
}

export function removeAllSubCatLevels() {
  return { type: REMOVE_ALL_SUB_CAT_LEVELS };
}

export function setSchedule(schedule) {
  return { type: SET_SCHEDULE, schedule };
}

export function setContractYear(year) {
  return { type: SET_CONTRACT_YEAR, year };
}

export function setQueryType(queryType) {
  return { type: SET_QUERY_TYPE, queryType };
}

export function setSite(site) {
  return { type: SET_SITE, site };
}

export function setSinNumber(sinNumber) {
  return { type: SET_SIN_NUMBER, sinNumber };
}

export function setSecurityClearance(securityClearance) {
  return { type: SET_SECURITY_CLEARANCE, securityClearance };
}

export function setBusinessSize(size) {
  return { type: SET_BUSINESS_SIZE, size };
}

export function setQuery(query) {
  return { type: SET_QUERY, query };
}

export function setQueryBy(queryBy) {
  return { type: SET_QUERY_BY, queryBy };
}
