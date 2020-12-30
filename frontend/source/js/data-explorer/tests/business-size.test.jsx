import toJson from 'enzyme-to-json';

import { BusinessSize } from '../components/business-size';
import { BUSINESS_SIZE_LABELS } from '../constants';
import makeSetup from './testSetup';

const defaultProps = {
  size: 'o',
  setSize: jest.fn(),
  idPrefix: 'zzz_',
};

const setup = makeSetup(BusinessSize, defaultProps);

describe('<BusinessSize>', () => {
  it('renders correctly', () => {
    const { wrapper } = setup();
    expect(wrapper.find('select').exists()).toBeTruthy();

    const allOption = wrapper.find('option[value=""]');
    expect(allOption.exists()).toBeTruthy();
    expect(allOption.text()).toBe('(all)');

    expect(wrapper.find('select').prop('value')).toBe('o');

    Object.keys(BUSINESS_SIZE_LABELS).forEach((key) => {
      const val = BUSINESS_SIZE_LABELS[key];
      const option = wrapper.find(`option[value="${key}"]`);
      expect(option.exists()).toBeTruthy();
      expect(option.text()).toBe(val);
    });
  });

  it('prefixes select id with idPrefix', () => {
    const { props, wrapper } = setup();
    expect(wrapper.find(`select#${props.idPrefix}business_size`).exists()).toBeTruthy();
  });

  it('applies filter_active based on size prop', () => {
    let { wrapper } = setup({ size: '' });
    expect(wrapper.find('select').hasClass('filter_active')).toBeFalsy();

    ({ wrapper } = setup({ size: 'contractor' }));
    expect(wrapper.find('select').hasClass('filter_active')).toBeTruthy();
  });

  it('calls setSize on change', () => {
    const { props, mounted } = setup();
    expect(props.setSize.mock.calls.length).toBe(0);

    mounted.find('select')
      .simulate('change', { target: { value: 's' } });

    expect(props.setSize.mock.calls.length).toBe(1);
    expect(props.setSize.mock.calls[0][0]).toBe('s');
  });

  it('matches snapshot', () => {
    const { wrapper } = setup({ size: 'contractor' });
    expect(toJson(wrapper)).toMatchSnapshot();
  });
});
