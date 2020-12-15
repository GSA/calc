import toJson from 'enzyme-to-json';
import { EducationLevel } from '../components/education-level';
import makeSetup from './testSetup';
import { EDU_LABELS } from '../constants';

const defaultProps = {
  levels: ['MA', 'PHD'],
  idPrefix: 'zzz_',
  toggleEducationLevel: jest.fn(),
};

const setup = makeSetup(EducationLevel, defaultProps);

describe('<EducationLevel>', () => {
  it('renders correctly', () => {
    const { wrapper } = setup();

    wrapper.setState({ expanded: true });

    Object.keys(EDU_LABELS).forEach((key) => {
      const eduLevelItem = wrapper.find(`EducationLevelItem[value="${key}"]`);
      expect(eduLevelItem.exists()).toBeTruthy();

      const id = `zzz_${key}`;
      expect(eduLevelItem.prop('id')).toBe(id);

      if (defaultProps.levels.indexOf(key) >= 0) {
        expect(eduLevelItem.prop('checked')).toBeTruthy();
      } else {
        expect(eduLevelItem.prop('checked')).toBeFalsy();
      }
    });
  });

  it('matches snapshot', () => {
    const { wrapper } = setup();
    wrapper.setState({ expanded: true });
    expect(toJson(wrapper)).toMatchSnapshot();
  });

  it('has filter_active class when levels are selected', () => {
    let { wrapper } = setup({ levels: [] });
    expect(wrapper.find('a.filter_active').exists()).toBeFalsy();

    ({ wrapper } = setup({ levels: ['HS'] }));
    expect(wrapper.find('a.filter_active').exists()).toBeTruthy();
  });

  it('calls toggleEducationLevel when checkbox is clicked', () => {
    const { props, mounted } = setup();
    expect(props.toggleEducationLevel.mock.calls.length).toBe(0);

    mounted.setState({ expanded: true });

    mounted.find('input[value="HS"]')
      .simulate('change', { target: { checked: true } });

    expect(props.toggleEducationLevel.mock.calls.length).toBe(1);
    expect(props.toggleEducationLevel.mock.calls[0][0]).toBe('HS');
  });

  it('fires handleToggleMenu when dropdown is clicked', () => {
    const { wrapper } = setup();
    const e = {
      preventDefault: jest.fn(),
    };
    expect(wrapper.state().expanded).toBeFalsy();
    wrapper.find('a').simulate('click', e);
    expect(wrapper.state().expanded).toBeTruthy();
  });
});
