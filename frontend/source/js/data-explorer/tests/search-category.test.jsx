import toJson from 'enzyme-to-json';

import { SearchCategory } from '../components/search-category';
import makeSetup from './testSetup';

const defaultProps = {
  selectedSchedule: '',
  queryBy: 'stuff and things',
};

const setup = makeSetup(SearchCategory, defaultProps, { wrapperOnly: true });

describe('<SearchCategory>', () => {
  it('renders correctly', () => {
    const { wrapper } = setup();
    const trigger = wrapper.find('.html-dropdown__trigger');
    expect(trigger.exists()).toBeTruthy();
    const dropdown = wrapper.find('.html-dropdown__choices');
    expect(dropdown.exists()).toBeTruthy();
  });

  it('matches snapshot', () => {
    const { wrapper } = setup();
    expect(toJson(wrapper)).toMatchSnapshot();
  });
});
