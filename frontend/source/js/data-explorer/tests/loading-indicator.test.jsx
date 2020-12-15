import toJson from 'enzyme-to-json';

import { LoadingIndicator } from '../components/loading-indicator';
import makeSetup from './testSetup';

const defaultProps = {
  error: null,
  inProgress: false,
};

const setup = makeSetup(LoadingIndicator, defaultProps);

describe('<LoadingIndicator>', () => {
  it('renders correctly', () => {
    const { wrapper } = setup();
    expect(wrapper.find('.loading-indicator').exists()).toBeTruthy();
    expect(wrapper.find('.usa-sr-only').exists()).toBeTruthy();
  });

  it('matches snapshot', () => {
    const { wrapper } = setup();
    expect(toJson(wrapper)).toMatchSnapshot();
  });

  it('renders error message', () => {
    const { wrapper } = setup({ error: 'an error message' });
    expect(wrapper.find('.error-message').text()).toBe('an error message');
    expect(wrapper.find('.usa-sr-only').text())
      .toBe('An error occurred when loading results: an error message');
  });

  it('does not render an "abort" error message', () => {
    const { wrapper } = setup({ error: 'abort' });
    expect(wrapper.find('.error-message').exists()).toBeFalsy();
  });

  it('changes aria status based on inProgress', () => {
    let { wrapper } = setup({ inProgress: false, error: null });
    expect(wrapper.find('.usa-sr-only').text()).toBe('Results loaded.');

    ({ wrapper } = setup({ inProgress: true }));
    expect(wrapper.find('.usa-sr-only').text()).toBe('Loading results');
  });
});
