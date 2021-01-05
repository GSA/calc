/**
 * This module provides functionality that makes it possible
 * to synchronize the current URL's querystring with the current
 * state of the Redux store via the HTML5 History API.
 *
 * This ultimately allows users to treat every change of a
 * search parameter in the Data Explorer as a separate page view,
 * thus allowing them to use their browser's back button to
 * undo changes to their search query. It also allows them to
 * easily share their searches with others.
 */

import * as querystring from 'querystring';

import {
  setState,
} from './actions';

import {
  autobind,
  parseQueryString,
} from './util';

import {
  allFields,
  serializers,
  deserializers,
  getChangedSerializedFields,
} from './serialization';

export default class StoreHistorySynchronizer {
  constructor(window) {
    autobind(this, ['reflectToHistoryMiddleware']);

    this.window = window;
    this.isReflectingToStore = false;
    this.onLocationChanged = () => {};
  }

  initialize(store, onLocationChanged) {
    this.onLocationChanged = onLocationChanged;
    this.window.addEventListener('popstate', () => {
      this.reflectToStore(store);
      this.onLocationChanged();
    });
    this.reflectToStore(store);
  }

  reflectToStore(store) {
    const qsFields = parseQueryString(
      this.window.location.search.substring(1)
    ); // substring after '?' char

    const state = store.getState();
    const changes = {};

    allFields.forEach((field) => {
      const oldVal = serializers[field](state[field]);
      const newDeserializedVal = deserializers[field](qsFields[field]);
      const newVal = serializers[field](newDeserializedVal);

      if (oldVal !== newVal) {
        changes[field] = newDeserializedVal;
      }
    });

    if (Object.keys(changes).length) {
      this.isReflectingToStore = true;
      store.dispatch(setState(Object.assign({}, state, changes)));
      this.isReflectingToStore = false;
    }
  }

  reflectToHistoryMiddleware(store) {
    const defaultState = store.getState();

    return next => (action) => {
      const oldState = store.getState();
      const result = next(action);
      const newState = store.getState();
      const changed = allFields.some(
        field => newState[field] !== oldState[field],
      );

      if (changed && !this.isReflectingToStore) {
        const nonDefaultFields = getChangedSerializedFields(
          defaultState,
          newState,
          allFields,
        );

        const qs = querystring.stringify(nonDefaultFields);

        this.window.history.pushState(null, null, `?${qs}`);
        this.onLocationChanged();
      }

      return result;
    };
  }
}
