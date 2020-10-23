import toJson from 'enzyme-to-json';

import { Site } from '../components/site';
import { SITE_LABELS } from '../constants';
import makeSetup from './testSetup';

const defaultProps = {
  site: 'contractor',
  setSite: jest.fn(),
  idPrefix: 'zzz_',
};

const setup = makeSetup(Site, defaultProps);

describe('<Site>', () => {
  it('renders correctly', () => {
    const { wrapper } = setup();
    expect(wrapper.find('select').exists()).toBeTruthy();

    const allOption = wrapper.find('option[value=""]');
    expect(allOption.exists()).toBeTruthy();
    expect(allOption.text()).toBe('(all)');

    expect(wrapper.find('select').prop('value')).toBe('contractor');

    Object.keys(SITE_LABELS).forEach((key) => {
      const val = SITE_LABELS[key];
      const option = wrapper.find(`option[value="${key}"]`);
      expect(option.exists()).toBeTruthy();
      expect(option.text()).toBe(val);
    });
  });

  it('prefixes select id with idPrefix', () => {
    const { props, wrapper } = setup();
    expect(wrapper.find(`select#${props.idPrefix}site`).exists()).toBeTruthy();
  });

  it('applies filter_active based on site prop', () => {
    let { wrapper } = setup({ site: '' });
    expect(wrapper.find('select').hasClass('filter_active')).toBeFalsy();

    ({ wrapper } = setup({ site: 'contractor' }));
    expect(wrapper.find('select').hasClass('filter_active')).toBeTruthy();
  });

  it('calls setSite on change', () => {
    const { props, mounted } = setup();
    expect(props.setSite.mock.calls.length).toBe(0);

    mounted.find('select')
      .simulate('change', { target: { value: 'customer' } });

    expect(props.setSite.mock.calls.length).toBe(1);
    expect(props.setSite.mock.calls[0][0]).toBe('customer');
  });

  it('matches snapshot', () => {
    const { wrapper } = setup();
    expect(toJson(wrapper)).toMatchSnapshot();
  });
});
