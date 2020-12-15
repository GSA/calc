import toJson from 'enzyme-to-json';

import { ExportData } from '../components/export-data';
import { API_PATH_RATES_CSV } from '../api';

import makeSetup from './testSetup';


const defaultProps = {
  querystring: '?hi=james',
};

const setup = makeSetup(ExportData, defaultProps);

describe('<ExportData>', () => {
  it('renders correctly', () => {
    const { props, wrapper } = setup();
    const anchor = wrapper.find('a.export-data');
    expect(anchor.exists()).toBeTruthy();
    /* eslint-disable */
    expect(anchor.prop('href')).toBe(`${window.API_HOST}${API_PATH_RATES_CSV}/${props.querystring}`);
    /* eslint-enable */
  });

  it('matches snapshot', () => {
    const { wrapper } = setup();
    expect(toJson(wrapper)).toMatchSnapshot();
  });
});
