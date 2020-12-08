import toJson from 'enzyme-to-json';

import { Description } from '../components/description';
import makeSetup from './testSetup';

const defaultProps = {
  shownResults: 101,
  totalResults: 5000,
  minExperience: 5,
  maxExperience: 10,
  education: ['High School'],
  site: 'both',
  businessSize: 's',
  schedule: 'IT Schedule 70',
  laborCategory: 'Systems Analyst',
};

const setup = makeSetup(Description, defaultProps);

describe('<Description>', () => {
  // Just testing against the snapshot for this component since
  // it doesn't really have any interactivity
  it('matches snapshot', () => {
    const { wrapper } = setup();
    expect(toJson(wrapper)).toMatchSnapshot();
  });
});
