import { spy } from 'sinon';

import StoreRatesAutoRequester, { getRatesParameters } from '../rates-request';

import { HISTOGRAM_BINS } from '../constants';
import { START_RATES_REQUEST } from '../actions';

const MOCK_STATE = {
  exclude: [4, 8, 16],
  q: 'designer',
  education: ['BA', 'PHD'],
  min_experience: 0,
  max_experience: 45,
  'contract-year': 'current',
  site: 'both',
  business_size: 's',
  schedule: 'IT Schedule 70',
  sort: {
    key: 'current_price',
    descending: false,
  },
  query_type: 'match_all',
};

describe('getRatesParameters()', () => {
  it('serializes all parameters', () => {
    const state = Object.assign({}, MOCK_STATE);

    const res = getRatesParameters(state);

    expect(res).toMatchObject({
      q: 'designer',
      site: 'both',
      education: 'BA,PHD',
      exclude: '4,8,16',
      experience_range: '0,45',
      business_size: 's',
      schedule: 'IT Schedule 70',
      max_experience: '45',
      min_experience: '0',
      query_type: 'match_all',
      sort: 'current_price',
    });
  });
});

describe('StoreRatesAutoRequester middleware', () => {
  it('exposes a Redux middleware that performs rates requests', () => {
    const mockApi = {
      get: spy(),
    };

    const requester = new StoreRatesAutoRequester(mockApi);

    const origState = Object.assign({}, MOCK_STATE);

    const nextState = Object.assign({
      rates: {
        stale: true,
      },
    }, MOCK_STATE);
    nextState.q = 'engineer'; // change a field

    let nextCalled = false;

    const mockStore = {
      dispatch: spy(),
      getState: () => {
        if (nextCalled) { return nextState; }
        return origState;
      },
    };

    const middlewareFunc = requester.middleware(mockStore);

    const fakeAction = 'my-action';

    const mockNext = (action) => {
      nextCalled = true;
      if (action === fakeAction) {
        return 'fake-result';
      }
      return null;
    };

    const res = middlewareFunc(mockNext)(fakeAction);
    expect(res).toEqual('fake-result');

    expect(mockApi.get.calledOnce).toBeTruthy();
    expect(mockApi.get.calledWith({
      uri: '/rates',
      data: {
        histogram: HISTOGRAM_BINS,
        exclude: '4,8,16',
        education: 'BA,PHD',
        q: 'engineer',
        site: 'both',
        business_size: 's',
        schedule: 'IT Schedule 70',
        min_experience: '0',
        max_experience: '45',
        sort: 'current_price',
        query_type: 'match_all',
        experience_range: '0,45',
      },
    })).toBeTruthy();

    expect(mockStore.dispatch.calledWith(
      { type: START_RATES_REQUEST }
    )).toBeTruthy();
  });
});
