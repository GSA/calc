import toJson from 'enzyme-to-json';

import { MAX_QUERY_LENGTH, QUERY_TYPE_MATCH_ALL } from '../constants';
import { LaborCategory } from '../components/labor-category';
import makeSetup from './testSetup';

const defaultProps = {
  idPrefix: 'zzz_',
  query: '',
  queryType: QUERY_TYPE_MATCH_ALL,
  setQuery: jest.fn(),
  api: {},
};

const setup = makeSetup(LaborCategory, defaultProps);

jest.mock('../autocomplete');

describe('<LaborCategory>', () => {
  it('renders correctly', () => {
    const { props, wrapper } = setup();
    const input = wrapper.find(`input[type="text"][id="${props.idPrefix}labor_category"]`);
    expect(input.exists()).toBeTruthy();
    expect(input.prop('maxLength')).toBe(MAX_QUERY_LENGTH);
  });

  it('matches snapshot', () => {
    const { wrapper } = setup();
    expect(toJson(wrapper)).toMatchSnapshot();
  });

  //   it('calls setQuery on enter', () => {
  //     const { props, mounted } = setup();
  //     expect(props.setQuery.mock.calls.length).toBe(0);

  //     const input = mounted.find('#zzz_labor_category');
  //     input.prop('value', 'newquery');
  //     input.simulate('change', { target: { value: 'newquery' } });
  //     input.simulate('keyDown', { key: 'Enter', keyCode: 13, which: 13 });

  //     expect(props.setQuery.mock.calls.length).toBe(1);
  //     expect(props.setQuery.mock.calls[0][0]).toBe('newquery');
  //   });
});
