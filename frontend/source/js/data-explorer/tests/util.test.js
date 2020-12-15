import * as util from '../util';

describe('util.formatFriendlyPrice()', () => {
  it('should return price w/o cents if price is integral', () => {
    expect(util.formatFriendlyPrice(1)).toBe('1');
  });

  it('should return price w/ cents if price is float', () => {
    expect(util.formatFriendlyPrice(1.1)).toBe('1.10');
  });
});

describe('util.getLastCommaSeparatedTerm()', () => {
  it('works', () => {
    expect(util.getLastCommaSeparatedTerm('foo')).toBe('foo');
    expect(util.getLastCommaSeparatedTerm('foo,bar')).toBe('bar');
    expect(util.getLastCommaSeparatedTerm('foo, bar')).toBe('bar');
    expect(util.getLastCommaSeparatedTerm('foo , bar')).toBe('bar');
    expect(util.getLastCommaSeparatedTerm('foo bar')).toBe('foo bar');
  });
});

describe('util.parseQueryString()', () => {
  it('works', () => {
    expect(util.parseQueryString('a=1&b=cow')).toEqual({ a: '1', b: 'cow' });
  });

  it('uses first value of a repeated param', () => {
    expect(util.parseQueryString('z=yes&z=no')).toEqual({ z: 'yes' });
    expect(util.parseQueryString('x=&x=')).toEqual({ x: '' });
  });
});
