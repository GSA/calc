import toJson from 'enzyme-to-json';

import DescriptionFilter from '../components/description-filter';
import makeSetup from './testSetup';

const defaultProps = {
  extraClassName: 'extra-class',
  label: 'A Label',
  children: 'children',
};

const setup = makeSetup(DescriptionFilter, defaultProps);

describe('<DescriptionFilter>', () => {
  // Just testing against the snapshot for this component since
  // it doesn't really have any interactivity
  it('matches snapshot', () => {
    const { wrapper } = setup();
    expect(toJson(wrapper)).toMatchSnapshot();
  });
});
