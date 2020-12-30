import toJson from 'enzyme-to-json';

import { QueryType } from '../components/query-type';
import makeSetup from './testSetup';

const defaultProps = {
  queryType: 'match_exact',
  setQueryType: jest.fn(),
  idPrefix: 'zzz_',
};

const setup = makeSetup(QueryType, defaultProps);

describe('<QueryType>', () => {
  it('renders correctly', () => {
    const { wrapper } = setup();
    expect(wrapper.find('#zzz_match_exact').prop('value')).toBe('match_exact');
  });

  it('matching queryType is checked', () => {
    const { wrapper } = setup();
    expect(wrapper.find('#zzz_match_exact').prop('checked')).toBe(true);
  });

  it('calls setQueryType fn onChange', () => {
    const { props, mounted } = setup();
    expect(props.setQueryType.mock.calls.length).toBe(0);
    mounted.find('#zzz_match_exact')
      .simulate('change', { target: { checked: true } });
    expect(props.setQueryType.mock.calls.length).toBe(1);
    expect(props.setQueryType.mock.calls[0][0]).toBe('match_exact');
  });

  it('matches snapshot', () => {
    const { wrapper } = setup();
    expect(toJson(wrapper)).toMatchSnapshot();
  });
});
