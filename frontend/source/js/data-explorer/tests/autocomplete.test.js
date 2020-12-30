import { processResults } from '../autocomplete';

describe('autocomplete.processResults', () => {
  const makeResults = () => [
    { labor_category: 'barista', count: 5, unused: 'blah' },
    { labor_category: 'chimney sweep', count: 2, unused: 'bloop' },
  ];

  it('should return [] if result undefined', () => {
    const r = processResults(undefined);
    expect(r).toBeInstanceOf(Array);
    expect(r.length).toBe(0);
  });

  it('should return [] if result is empty', () => {
    const r = processResults([]);
    expect(r).toBeInstanceOf(Array);
    expect(r.length).toBe(0);
  });

  it('should return formatted categories', () => {
    const r = processResults(makeResults());
    expect(r).toEqual(expect.arrayContaining([
      { term: 'barista', count: 5 },
      { term: 'chimney sweep', count: 2 },
    ]));
    expect(r.length).toBe(2);
  });
});
