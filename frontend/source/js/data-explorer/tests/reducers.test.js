import * as reducers from '../reducers';

import { MAX_QUERY_LENGTH } from '../constants';
import { SET_QUERY } from '../actions';

describe('reducers.q()', () => {
  it('truncates to MAX_QUERY_LENGTH', () => {
    const query = Array(MAX_QUERY_LENGTH + 5).join('x');
    const result = reducers.q('', { type: SET_QUERY, query });
    expect(result).toHaveLength(MAX_QUERY_LENGTH);
    expect(result).toMatch(Array(MAX_QUERY_LENGTH).join('x'));
  });
});
