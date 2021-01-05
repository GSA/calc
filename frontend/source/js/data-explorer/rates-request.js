/**
 * This module provides a Redux middleware that watches the store
 * for any state changes that would necessitate the fetching of
 * rates data from the server. If new data is needed, it will
 * automatically be requested from the server.
 */

import {
  startRatesRequest,
  completeRatesRequest,
} from './actions';

import {
  HISTOGRAM_BINS,
} from './constants';

import {
  autobind,
} from './util';

import {
  allFields,
  getSerializedFields,
} from './serialization';

import { API_PATH_RATES } from './api';

const nonRatesFields = ['proposed-price', 'contract-year'];
const ratesFields = allFields.filter(f => nonRatesFields.indexOf(f) === -1);

export function getRatesParameters(state) {
  const data = getSerializedFields(state, ratesFields, {
    omitEmpty: true,
  });
  return Object.assign(data, {
    experience_range: `${data.min_experience},${data.max_experience}`,
  });
}

export default class StoreRatesAutoRequester {
  constructor(api) {
    this.api = api;
    this.request = null;
    autobind(this, ['middleware']);
  }

  _startRatesRequest(store) {
    if (this.request) {
      this.request.abort();
    }
    const data = getRatesParameters(store.getState());
    const defaults = {
      histogram: HISTOGRAM_BINS,
    };

    store.dispatch(startRatesRequest());
    this.request = this.api.get({
      uri: API_PATH_RATES,
      data: Object.assign(defaults, data),
    }, (error, res) => {
      this.request = null;

      store.dispatch(completeRatesRequest(error, res));
    });
  }

  middleware(store) {
    return next => (action) => {
      const oldState = store.getState();
      const result = next(action);
      const newState = store.getState();
      const updated = ratesFields.some(
        field => newState[field] !== oldState[field],
      );

      if (updated || newState.rates.stale) {
        this._startRatesRequest(store);
      }

      return result;
    };
  }
}
