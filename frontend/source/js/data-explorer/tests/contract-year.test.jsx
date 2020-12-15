import toJson from 'enzyme-to-json';

import { ContractYear } from '../components/contract-year';
import makeSetup from './testSetup';

const defaultProps = {
  contractYear: 'current',
  setContractYear: jest.fn(),
  idPrefix: 'zzz_',
};

const setup = makeSetup(ContractYear, defaultProps);

// Mocking the Tooltip component (which is used in ContractYear)
// since the global $ causes problems in it when testing without jQuery loaded
jest.mock('../components/tooltip');

describe('<ContractYear>', () => {
  it('renders correctly', () => {
    const { props, wrapper } = setup();

    const curr = wrapper.find(`input[type="radio"][id="${props.idPrefix}current-year"]`);
    expect(curr.exists()).toBeTruthy();
    expect(curr.prop('value')).toBe('current');

    const oneYear = wrapper.find(`input[type="radio"][id="${props.idPrefix}one-year-out"]`);
    expect(oneYear.exists()).toBeTruthy();
    expect(oneYear.prop('value')).toBe('1');

    const twoYears = wrapper.find(`input[type="radio"][id="${props.idPrefix}two-years-out"]`);
    expect(twoYears.exists()).toBeTruthy();
    expect(twoYears.prop('value')).toBe('2');
  });

  it('calls setContractYear on change', () => {
    const { props, mounted } = setup();
    expect(props.setContractYear.mock.calls.length).toBe(0);

    mounted.find('#zzz_one-year-out')
      .simulate('change', { target: { value: '1' } });

    expect(props.setContractYear.mock.calls.length).toBe(1);
    expect(props.setContractYear.mock.calls[0][0]).toBe('1');
  });

  it('matches snapshot', () => {
    const { wrapper } = setup();
    expect(toJson(wrapper)).toMatchSnapshot();
  });
});
