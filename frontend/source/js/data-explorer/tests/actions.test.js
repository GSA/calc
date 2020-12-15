import * as actions from '../actions';

describe('actions', () => {
  it('should create an action to exclude a row', () => {
    const rowId = 12345;
    expect(actions.excludeRow(rowId)).toEqual({
      type: actions.EXCLUDE_ROW,
      rowId,
    });
  });

  it('should create an action to exclude none', () => {
    expect(actions.excludeNone()).toEqual({
      type: actions.EXCLUDE_NONE,
    });
  });
});
