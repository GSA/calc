/* eslint-disable no-unused-vars */
/* global window */

import xhr from 'xhr';
import sinon from 'sinon';

import API, {
  API_BASE, API_PATH_RATES_CSV,
  API_PATH_RATES, API_PATH_SEARCH,
} from '../api';

describe('API constants', () => {
  it('equal expected values', () => {
    expect(API_BASE).toEqual('/api');
    expect(API_PATH_RATES_CSV).toEqual('/rates/csv');
    expect(API_PATH_RATES).toEqual('/rates');
    expect(API_PATH_SEARCH).toEqual('/search');
  });
});

describe('API constructor', () => {
  it('defaults to API_BASE path', () => {
    const api = new API();
    expect(api.basePath).toMatch(`${API_BASE}`);
  });

  it('allows setting of basePath in constructor', () => {
    const api = new API('/api/v1');
    expect(api.basePath).toMatch('/api/v1');

    const api2 = new API('/api2/');
    expect(api2.basePath).toMatch('/api2');
  });
});

describe('API get', () => {
  xhr.XMLHttpRequest = sinon.FakeXMLHttpRequest;
  const api = new API();
  let req;

  beforeEach(() => {
    req = null;
  });

  const resHeaders = {
    'Content-Type': 'application/json',
  };

  sinon.FakeXMLHttpRequest.onCreate = (xhrObj) => {
    if (req) {
      throw new Error('more than one request made in this test!');
    }
    req = xhrObj;
  };

  it('works with just uri', (done) => {
    api.get({ uri: '/whatever' }, (err, res) => {
      expect(err).toBeFalsy();
      expect(res).toMatchObject({ result: 'success' });
      done();
    });
    expect(req.url).toEqual(`${API_BASE}/whatever`);
    req.respond(200, resHeaders, JSON.stringify({ result: 'success' }));
  });

  it('works with uri and data object', (done) => {
    api.get({ uri: '/data', data: { param: 'value' } }, (err, res) => {
      expect(err).toBeFalsy();
      expect(res).toMatchObject({ result: 'data_success' });
      done();
    });
    expect(req.url).toEqual(`${API_BASE}/data?param=value`);
    req.respond(200, resHeaders, JSON.stringify({ result: 'data_success' }));
  });


  it('callsback with string on error response', (done) => {
    api.get({ uri: '/bad' }, (err, res) => {
      expect(res).toBeFalsy();
      expect(err).toMatch('Not Found');
      done();
    });
    req.respond(404, resHeaders);
  });


  it('callsback with a string on network error', (done) => {
    api.get({ uri: '/network_error' }, (err, res) => {
      expect(res).toBeFalsy();
      expect(err).toMatch('Error: Internal XMLHttpRequest Error');
      done();
    });
    req.error();
  });
});
