import toJson from 'enzyme-to-json';
import React from 'react';
import { mount } from 'enzyme';

import Tooltip from '../components/tooltip';

const defaultProps = {
  children: '',
  text: 'hi james',
  show: false,
};

const tooltipsterMock = jest.fn().mockReturnThis();

// mock the global jquery object function used in <Tooltip>
global.$ = () => {
  const m = jest.fn();
  m.tooltipster = tooltipsterMock;
  return m;
};

describe('<Tooltip>', () => {
  // NOTE: This test does not cover any tooltipster functionality,
  // which has all been mocked
  it('matches snapshot', () => {
    const component = React.createElement(Tooltip, defaultProps);
    const mounted = mount(component);
    expect(toJson(mounted)).toMatchSnapshot();
  });

  it('initializes tooltipster', () => {
    const component = React.createElement(Tooltip, defaultProps);
    mount(component);
    expect(tooltipsterMock.mock.calls.length).toBeGreaterThan(0);
  });
});
