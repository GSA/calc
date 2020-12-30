import React from 'react';
import { shallow } from 'enzyme';
import toJson from 'enzyme-to-json';

import LoadableWrapper, { Loading } from '../components/loadable-wrapper';
import makeSetup from './testSetup';


describe('LoadableWrapper', () => {
  const makeFakeLoader = () => () => Promise.resolve(() => 'hello!');

  it('creates a react-loadable higher-order component', () => {
    const LoadableTestComponent = LoadableWrapper(makeFakeLoader());

    const wrapper = shallow(<LoadableTestComponent />);
    expect(wrapper.exists()).toBeTruthy();
    expect(toJson(wrapper)).toMatchSnapshot();
  });
});

describe('<Loading>', () => {
  const defaultProps = {
    error: null,
    pastDelay: false,
  };

  const setup = makeSetup(Loading, defaultProps);

  it('renders nothing by default', () => {
    const { wrapper } = setup();
    expect(wrapper.text()).toEqual('');
  });

  it('renders an alert if there is an error', () => {
    const { wrapper } = setup({ error: new Error('boop') });
    expect(wrapper.find('.usa-alert-error').exists()).toBeTruthy();
    expect(toJson(wrapper)).toMatchSnapshot();
  });

  it('renders a loading state if pastDelay', () => {
    const { wrapper } = setup({ pastDelay: true });
    expect(wrapper.text()).toEqual('Loading...');
    expect(toJson(wrapper)).toMatchSnapshot();
  });
});
