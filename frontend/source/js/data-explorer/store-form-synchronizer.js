import { setState } from './actions';

import {
  EDU_LABELS,
  MIN_EXPERIENCE,
  MAX_EXPERIENCE,
  SITE_LABELS,
  BUSINESS_SIZE_LABELS,
  SCHEDULE_LABELS,
  CONTRACT_YEAR_LABELS,
  DEFAULT_CONTRACT_YEAR,
  DEFAULT_SORT,
  DEFAULT_QUERY_TYPE,
  QUERY_TYPE_LABELS,
} from './constants';

import {
  parsePrice,
} from './util';

const parseSort = val => {
  if (!val) {
    return DEFAULT_SORT;
  }

  // TODO: Ensure the key is valid.

  if (val.charAt(0) === '-') {
    return { key: val.substr(1), descending: true };
  }
  return { key: val, descending: false };
};

const coercedString = val => {
  if (val === undefined) {
    return '';
  }
  return String(val);
};

const coercedExperience = defaultVal => val => {
  const valInt = parseInt(val, 10);

  if (isNaN(valInt)) {
    return defaultVal;
  }

  return Math.max(Math.min(valInt, MAX_EXPERIENCE), MIN_EXPERIENCE);
};

const stringInSet = (choices, defaultVal = '') => val => {
  if (val in choices) {
    return val;
  }

  return defaultVal;
};

const serializers = {
  exclude: list => list.map(coercedString).join(','),
  education: list => list.map(coercedString).join(','),
  q: coercedString,
  'contract-year': coercedString,
  site: coercedString,
  business_size: coercedString,
  schedule: coercedString,
  min_experience: coercedString,
  max_experience: coercedString,
  'proposed-price': coercedString,
  sort: ({ key, descending }) => (descending ? '-' : '') + key,
  query_type: coercedString,
};

const deserializers = {
  exclude: list =>
    coercedString(list)
      .split(',')
      .map(x => parseInt(x, 10))
      .filter(x => !isNaN(x)),
  education: list =>
    coercedString(list)
      .split(',')
      .filter(x => x in EDU_LABELS),
  q: coercedString,
  'contract-year': stringInSet(CONTRACT_YEAR_LABELS, DEFAULT_CONTRACT_YEAR),
  site: stringInSet(SITE_LABELS),
  business_size: stringInSet(BUSINESS_SIZE_LABELS),
  schedule: stringInSet(SCHEDULE_LABELS),
  min_experience: coercedExperience(MIN_EXPERIENCE),
  max_experience: coercedExperience(MAX_EXPERIENCE),
  'proposed-price': parsePrice,
  sort: parseSort,
  query_type: stringInSet(QUERY_TYPE_LABELS, DEFAULT_QUERY_TYPE),
};

const fields = Object.keys(serializers);

const nonRatesFields = ['proposed-price', 'contract-year'];

const ratesFields = fields.filter(f => nonRatesFields.indexOf(f) === -1);

function autobind(self, names) {
  const target = self;

  names.forEach(name => {
    target[name] = target[name].bind(target);
  });
}

export function StoreStateFieldWatcher() {
  const watchers = [];

  return {
    watch(name, cb) {
      watchers.push([name, cb]);
    },

    middleware(store) {
      return next => action => {
        const oldState = store.getState();
        const result = next(action);
        const newState = store.getState();

        watchers.forEach(([name, cb]) => {
          if (oldState[name] !== newState[name]) {
            cb();
          }
        });

        return result;
      };
    },
  };
}

export class StoreRatesAutoRequester {
  constructor() {
    autobind(this, ['middleware']);
  }

  initialize(store, onRatesRequest) {
    Object.assign(this, {
      onRatesRequest,
    });

    // TODO: We should make a separate action for loading rates
    // if invalid or something.
    store.dispatch(setState(Object.assign(store.getState())));
  }

  getRatesParameters(store) {
    const state = store.getState();
    const result = {};

    ratesFields.forEach(field => {
      const val = serializers[field](state[field]);

      if (val.length) {
        result[field] = val;
      }
    });

    return result;
  }

  middleware(store) {
    return next => action => {
      const oldState = store.getState();
      const result = next(action);
      const newState = store.getState();
      const updated = ratesFields.some(
        field => newState[field] !== oldState[field]
      );

      if (updated || newState.rates.stale) {
        this.onRatesRequest(store);
      }

      return result;
    };
  }
}

export class StoreFormSynchronizer {
  constructor(form) {
    this.form = form;

    autobind(this, ['reflectToFormMiddleware']);

    const nonReactFields = form.getInputs().map(e => e.getAttribute('name'));

    this.fields = fields.filter(f => nonReactFields.indexOf(f) >= 0);
  }

  reflectToFormMiddleware(store) {
    return next => action => {
      const result = next(action);
      const state = store.getState();

      // TODO: Remove this logging line eventually.
      console.log(state);  // eslint-disable-line

      this.fields.forEach(field => {
        const oldVal = serializers[field](
          deserializers[field](this.form.get(field))
        );
        const newVal = serializers[field](state[field]);

        if (oldVal !== newVal) {
          this.form.set(field, newVal);
        }
      });

      return result;
    };
  }

  reflectToStore(store) {
    const state = store.getState();
    const changes = {};

    this.fields.forEach(field => {
      const oldVal = serializers[field](state[field]);
      const newSerializedVal = deserializers[field](this.form.get(field));
      const newVal = serializers[field](newSerializedVal);

      if (oldVal !== newVal) {
        changes[field] = newSerializedVal;
      }
    });

    if (Object.keys(changes).length) {
      store.dispatch(setState(Object.assign({}, state, changes)));
    }
  }
}
