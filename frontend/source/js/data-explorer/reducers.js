import { combineReducers } from 'redux';

import {
  MIN_EXPERIENCE,
  MAX_EXPERIENCE,
  DEFAULT_CONTRACT_YEAR,
  EMPTY_RATES_DATA,
  DEFAULT_SORT,
  DEFAULT_QUERY_TYPE,
  QUERY_TYPE_MATCH_ALL,
  QUERY_TYPE_MATCH_EXACT,
  MAX_QUERY_LENGTH,
  DEFAULT_QUERY_BY,
} from './constants';

import {
  EXCLUDE_NONE,
  EXCLUDE_ROW,
  SET_STATE,
  RESET_STATE,
  COMPLETE_RATES_REQUEST,
  START_RATES_REQUEST,
  INVALIDATE_RATES,
  SET_SORT,
  SET_PROPOSED_PRICE,
  SET_EXPERIENCE,
  TOGGLE_EDU_LEVEL,
  TOGGLE_CAT_LEVEL,
  SET_SCHEDULE,
  SET_CONTRACT_YEAR,
  SET_QUERY_TYPE,
  SET_SITE,
  SET_BUSINESS_SIZE,
  SET_QUERY,
  SET_QUERY_BY,
  SET_SIN_NUMBER,
  SET_SECURITY_CLEARANCE,
} from './actions';

function exclude(state = [], action) {
  switch (action.type) {
    case EXCLUDE_NONE:
      return [];
    case EXCLUDE_ROW:
      return state.concat(action.rowId);
    default:
      return state;
  }
}

function contractYear(state = DEFAULT_CONTRACT_YEAR, action) {
  if (action.type === SET_CONTRACT_YEAR) {
    return action.year;
  }
  return state;
}

export function q(state = '', action) {
  if (action.type === SET_QUERY) {
    const cleanedQuery = action.query.slice(0, MAX_QUERY_LENGTH);
    return cleanedQuery;
  }
  return state;
}

function education(state = [], action) {
  console.log(action.type+"<-- ActionType: EDUCATiON ACTION SELECTED*************************************************"+action.level);
  if (action.type === TOGGLE_EDU_LEVEL) {
    if (state.indexOf(action.level) === -1) {
      return state.concat(action.level);
    }
    return state.filter(lvl => lvl !== action.level);
  }
  return state;
}

function categoryFunction(state = [], action) {
  console.log(JSON.stringify(action));
  console.log(action.type+"<-- ActionType: CATEGORY ACTION SELECTED*************************************************"+action.level);
  console.log(JSON.stringify(state));
  if (action.type === TOGGLE_CAT_LEVEL) {
    if (state.indexOf(action.level) === -1) {
      return state.concat(action.level);
    }
    return state.filter(lvl => lvl !== action.level);
  }
  return state;

}

function minExperience(state = MIN_EXPERIENCE, action) {
  if (action.type === SET_EXPERIENCE && action.subtype === 'min') {
    return action.years;
  }
  return state;
}

function maxExperience(state = MAX_EXPERIENCE, action) {
  if (action.type === SET_EXPERIENCE && action.subtype === 'max') {
    return action.years;
  }
  return state;
}

function site(state = '', action) {
  if (action.type === SET_SITE) {
    return action.site;
  }
  return state;
}

function businessSize(state = '', action) {
  if (action.type === SET_BUSINESS_SIZE) {
    return action.size;
  }
  return state;
}

function sinNumberFunction(state = '', action) {
  console.log(action.type+"<-- ActionType: SIN ACTION SELECTED*************************************************"+action.level);
  if (action.type === SET_SIN_NUMBER) {
    return action.sinNumber;
  }
  return state;
}

function securityClearence(state = '', action) {
  if (action.type === SET_SECURITY_CLEARANCE) {
    return action.securityClearance;
  }
  return state;
}

function schedule(state = '', action) {
  if (action.type === SET_SCHEDULE) {
    return action.schedule;
  }

  return state;
}

function proposedPrice(state = 0, action) {
  if (action.type === SET_PROPOSED_PRICE) {
    return action.price;
  }
  return state;
}

function rates(state = {
  error: null,
  data: EMPTY_RATES_DATA,
  inProgress: false,
  stale: true,
}, action) {
  const normalizeData = (d) => {
    if (d && d.results && d.results.length) {
      return d;
    }
    return EMPTY_RATES_DATA;
  };

  switch (action.type) {
    case START_RATES_REQUEST:
      return Object.assign({}, state, {
        inProgress: true,
        error: null,
        stale: false,
      });
    case COMPLETE_RATES_REQUEST:
      return {
        inProgress: false,
        error: action.error,
        data: normalizeData(action.data),
        stale: false,
      };
    case INVALIDATE_RATES:
      if (state.inProgress) {
        return state;
      }
      return Object.assign({}, state, {
        stale: true,
      });
    default:
      return state;
  }
}

function sort(state = DEFAULT_SORT, action) {
  if (action.type === SET_SORT) {
    return { key: action.key, descending: action.descending };
  }
  return state;
}

function queryType(state = DEFAULT_QUERY_TYPE, action) {
  if (action.type === SET_QUERY_TYPE) {
    // since the match_exact checkbox toggles these,
    // set the state equal to the opposite of what is currently set.
    if (action.queryType === QUERY_TYPE_MATCH_ALL) {
      return QUERY_TYPE_MATCH_EXACT;
    }
    return QUERY_TYPE_MATCH_ALL;
  }
  return state;
}

function queryBy(state = DEFAULT_QUERY_BY, action) {
  if (action.type === SET_QUERY_BY) {
    return action.queryBy || '';
  }
  return state;
}

const combinedReducer = combineReducers({
  exclude,
  q,
  education,
  category: categoryFunction,
  min_experience: minExperience,
  max_experience: maxExperience,
  'contract-year': contractYear,
  site,
  business_size: businessSize,
  sinNumber: sinNumberFunction,
  securityClearance: securityClearence,
  schedule,
  rates,
  'proposed-price': proposedPrice,
  sort,
  query_type: queryType,
  query_by: queryBy,
});

export default (state, action) => {
  if (action.type === SET_STATE) {
    return action.value;
  }
  if (action.type === RESET_STATE) {
    return combinedReducer(undefined, action);
  }
  return combinedReducer(state, action);
};
