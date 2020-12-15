import toJson from 'enzyme-to-json';

import EducationLevelItem from '../components/education-level-item';
import makeSetup from './testSetup';
import { EDU_LABELS } from '../constants';

const defaultProps = {
  id: 'zzz-item',
  value: 'AA',
  checked: true,
  onCheckboxClick: jest.fn(),
};

const setup = makeSetup(EducationLevelItem, defaultProps);

describe('<EducationLevelItem>', () => {
  it('renders correctly', () => {
    const { props, wrapper } = setup();

    const checkbox = wrapper.find('input[type="checkbox"]');
    expect(checkbox.exists()).toBeTruthy();

    const label = wrapper.find(`label[htmlFor="${props.id}"]`);
    expect(label.exists()).toBeTruthy();
    expect(label.text()).toBe(EDU_LABELS[props.value]);
  });

  it('matches snapshot', () => {
    const { wrapper } = setup();
    expect(toJson(wrapper)).toMatchSnapshot();
  });

  it('calls onCheckboxClick on change', () => {
    const { props, mounted } = setup();
    expect(props.onCheckboxClick.mock.calls.length).toBe(0);

    mounted.find('input').simulate('change',
      { target: { checked: !props.checked } });

    expect(props.onCheckboxClick.mock.calls.length).toBe(1);
  });
});
