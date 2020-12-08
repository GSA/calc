/* eslint-disable camelcase */

import {
  serializers, deserializers,
  getSerializedFields, getChangedSerializedFields,
} from '../serialization';
import {
  DEFAULT_SORT,
  DEFAULT_CONTRACT_YEAR,
  DEFAULT_QUERY_TYPE,
  DEFAULT_QUERY_BY,
  MAX_QUERY_LENGTH,
  MIN_EXPERIENCE,
  MAX_EXPERIENCE,
} from '../constants';


describe('serializers', () => {
  describe('sort serializer', () => {
    const { sort } = serializers;

    it('prepends "-" if descending', () => {
      expect(sort({ descending: true, key: 'blah' })).toBe('-blah');
    });

    it('does not prepend "-" if ascending', () => {
      expect(sort({ descending: false, key: 'blah' })).toBe('blah');
    });
  });
});

describe('deserializers', () => {
  describe('sort', () => {
    const { sort } = deserializers;

    it('returns default sort when invalid', () => {
      expect(sort('')).toEqual(DEFAULT_SORT);
      expect(sort('-')).toEqual(DEFAULT_SORT);
      expect(sort('LOL')).toEqual(DEFAULT_SORT);
      expect(sort('-LOL')).toEqual(DEFAULT_SORT);
    });

    it('returns descending sort when preceded by "-"', () => {
      expect(sort('-labor_category')).toEqual({
        key: 'labor_category',
        descending: true,
      });
    });

    it('returns ascending sort when not preceded by "-"', () => {
      expect(sort('vendor_name')).toEqual({
        key: 'vendor_name',
        descending: false,
      });
    });
  });

  describe('q', () => {
    const { q } = deserializers;

    it('truncates to the MAX_QUERY_LENGTH', () => {
      const longQuery = Array(MAX_QUERY_LENGTH + 5).join('a');
      expect(q(longQuery)).toHaveLength(MAX_QUERY_LENGTH);
    });
  });

  describe('min_experience', () => {
    it('deserializes various values', () => {
      const { min_experience } = deserializers;
      expect(min_experience('BOOP')).toBe(MIN_EXPERIENCE);
      expect(min_experience('5')).toBe(5);
      expect(min_experience(10)).toBe(10);
      expect(min_experience('22.1')).toBe(22);
      expect(min_experience(`${MAX_EXPERIENCE + 1}`)).toBe(MAX_EXPERIENCE);
      expect(min_experience(`${MIN_EXPERIENCE - 1}`)).toBe(MIN_EXPERIENCE);
    });
  });

  describe('max_experience', () => {
    it('deserializes various values', () => {
      const { max_experience } = deserializers;
      expect(max_experience('BOOP')).toBe(MAX_EXPERIENCE);
      expect(max_experience('5')).toBe(5);
      expect(max_experience(10)).toBe(10);
      expect(max_experience('22.1')).toBe(22);
      expect(max_experience(`${MAX_EXPERIENCE + 1}`)).toBe(MAX_EXPERIENCE);
      expect(max_experience(`${MIN_EXPERIENCE - 1}`)).toBe(MIN_EXPERIENCE);
    });
  });

  describe('exclude', () => {
    it('deserializes various values', () => {
      const { exclude } = deserializers;
      expect(exclude([])).toEqual([]);
      expect(exclude(['5,6,garbage,7,8,'])).toEqual([5, 6, 7, 8]);
    });
  });

  describe('education', () => {
    it('deserializes various values', () => {
      const { education } = deserializers;
      expect(education([])).toEqual([]);
      expect(education(['MA,PHD,XYZ,BA'])).toEqual(['MA', 'PHD', 'BA']);
    });
  });

  describe('schedule', () => {
    it('deserializes various values', () => {
      const { schedule } = deserializers;
      expect(schedule('whatever')).toBe('');
      expect(schedule('IT Schedule 70')).toBe('IT Schedule 70');
      expect(schedule('MOBIS')).toBe('MOBIS');
    });
  });

  describe('contract-year', () => {
    it('deserializes various values', () => {
      const contractYear = deserializers['contract-year'];
      expect(contractYear('whatever')).toBe(DEFAULT_CONTRACT_YEAR);
      expect(contractYear('current')).toBe('current');
      expect(contractYear('2')).toBe('2');
    });
  });

  describe('site', () => {
    it('deserializes various values', () => {
      const { site } = deserializers;
      expect(site('whatever')).toBe('');
      expect(site('customer')).toBe('customer');
      expect(site('both')).toBe('both');
    });
  });

  describe('business_size', () => {
    it('deserializes various values', () => {
      const { business_size } = deserializers;
      expect(business_size('whatever')).toBe('');
      expect(business_size('s')).toBe('s');
      expect(business_size('o')).toBe('o');
    });
  });

  describe('proposed-price', () => {
    it('deserializes various values', () => {
      const proposedPrice = deserializers['proposed-price'];
      expect(proposedPrice('whatever')).toBe(0);
      expect(proposedPrice('28')).toBe(28);
      expect(proposedPrice('101.20')).toBe(101.2);
    });
  });

  describe('query_type', () => {
    it('deserializes various values', () => {
      const { query_type } = deserializers;
      expect(query_type('whatever')).toBe(DEFAULT_QUERY_TYPE);
      expect(query_type('match_exact')).toBe('match_exact');
    });
  });

  describe('query_by', () => {
    it('deserializes various values', () => {
      const { query_by } = deserializers;
      expect(query_by('whatever')).toBe(DEFAULT_QUERY_BY);
      expect(query_by('vendor_name')).toBe('vendor_name');
    });
  });
});

describe('getSerializedFields()', () => {
  it('gets fields from state', () => {
    const state = {
      exclude: [5, 'boop'],
      education: ['BA', 'HS'],
      q: 'query',
      somethingElse: 'whatever', // not included in fields
    };

    const fields = ['exclude', 'education', 'q'];

    const res = getSerializedFields(state, fields);
    expect(res).toMatchObject({
      exclude: '5,boop',
      education: 'BA,HS',
      q: 'query',
    });
  });

  it('can omit empty fields', () => {
    const state = {
      q: 'the query',
      query_type: '',
      min_experience: '',
    };

    const fields = ['q', 'query_type', 'min_experience'];

    const opts = { omitEmpty: true };

    const res = getSerializedFields(state, fields, opts);
    expect(res).toMatchObject({
      q: 'the query',
    });
  });
});

describe('getChangedSerializedFields()', () => {
  it('returns only values that have changed in state', () => {
    const oldState = {
      q: 'old query',
      query_type: 'match_all',
      site: 'customer',
    };

    const newState = {
      q: 'new query',
      query_type: 'match_phrase',
      'proposed-price': '45.10',
      site: 'customer',
    };

    const fields = ['q', 'query_type', 'site', 'proposed-price'];

    const res = getChangedSerializedFields(oldState, newState, fields);

    expect(res).toMatchObject({
      q: newState.q,
      query_type: newState.query_type,
      'proposed-price': newState['proposed-price'],
    });

    // `site` should not be included
    expect(res.site).toBeUndefined();
  });
});
