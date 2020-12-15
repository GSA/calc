import toJson from 'enzyme-to-json';

import { Schedule } from '../components/schedule';
import makeSetup from './testSetup';
import { QUERY_BY_SCHEDULE } from '../constants';
import { scheduleLabels } from '../schedule-metadata';

const defaultProps = {
  selectedSchedule: '',
  queryBy: QUERY_BY_SCHEDULE,
  setSchedule: jest.fn(),
  setQueryBy: jest.fn(),
};

const setup = makeSetup(Schedule, defaultProps);

describe('<Schedule>', () => {
  it('renders correctly', () => {
    const { wrapper } = setup();
    const select = wrapper.find('.filter--schedule');
    expect(select.exists()).toBeTruthy();
    const options = wrapper.find('li');
    // should have options for all schedules + 1 for "(all)"
    expect(options.length).toBe(Object.keys(scheduleLabels).length + 1);
    Object.keys(scheduleLabels).forEach((sched) => {
      const opt = wrapper.find(`input[value="${sched}"]`);
      expect(opt.exists()).toBeTruthy();
    });
  });

  it('matches snapshot', () => {
    const { wrapper } = setup();
    expect(toJson(wrapper)).toMatchSnapshot();
  });

  it('calls setSchedule on change', () => {
    const { props, mounted } = setup();
    expect(props.setSchedule.mock.calls.length).toBe(0);

    mounted.find('#mobis')
      .simulate('change', { target: { value: 'MOBIS' } });

    expect(props.setSchedule.mock.calls.length).toBe(1);
    expect(props.setSchedule.mock.calls[0][0]).toBe('MOBIS');
  });
});
