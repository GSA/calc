import toJson from 'enzyme-to-json';

import { Vendor } from '../components/vendor-search';
import makeSetup from './testSetup';
import { QUERY_BY_VENDOR } from '../constants';

const defaultProps = {
  selectedSchedule: '',
  queryBy: 'spanish inquisition',
  setSchedule: jest.fn(),
  setQueryBy: jest.fn(),
};

const setup = makeSetup(Vendor, defaultProps);

describe('<Vendor>', () => {
  it('renders correctly', () => {
    const { wrapper } = setup();
    const trigger = wrapper.find(`#${QUERY_BY_VENDOR}`);
    expect(trigger.exists()).toBeTruthy();
  });

  it('calls setSchedule and setQueryBy on click', () => {
    const { props, mounted } = setup();
    expect(props.setSchedule.mock.calls.length).toBe(0);
    expect(props.setQueryBy.mock.calls.length).toBe(0);
    mounted.find(`#${QUERY_BY_VENDOR}`)
      .simulate('click');
    expect(props.setSchedule.mock.calls.length).toBe(1);
    expect(props.setQueryBy.mock.calls.length).toBe(1);
    expect(props.setSchedule.mock.calls[0][0]).toBe('');
    expect(props.setQueryBy.mock.calls[0][0]).toBe(QUERY_BY_VENDOR);
  });

  it('matches snapshot', () => {
    const { wrapper } = setup();
    expect(toJson(wrapper)).toMatchSnapshot();
  });
});
