import React from 'react';
import { mount } from 'enzyme';

import SlideyPanel from '../components/slidey-panel';

const fake$ = (el) => {
  const name = `<${el.nodeName.toLowerCase()}>`;

  return {
    hide() {
      fake$.log.push(`hide ${name}`);
      return this;
    },
    slideUp(speed, cb) {
      fake$.log.push(`slideUp ${name} ${speed}`);
      cb();
    },
    slideDown(speed, cb) {
      fake$.log.push(`slideDown ${name} ${speed}`);
      cb();
    },
  };
};

fake$.log = [];

describe('<SlideyPanel>', () => {
  beforeEach(() => {
    fake$.log = [];
  });

  it('shows content if it is expanded at mount', () => {
    const wrapper = mount(
      <SlideyPanel expanded>
        <p>
          hi
        </p>
      </SlideyPanel>
    );

    expect(wrapper.find('p').exists()).toBeTruthy();
    expect(wrapper.text()).toBe('hi');
  });

  it('hides content if it is not expanded at mount', () => {
    const wrapper = mount(
      <SlideyPanel>
        <p>
          hi
        </p>
      </SlideyPanel>
    );

    expect(wrapper.find('p').exists()).toBeFalsy();
  });

  it('shows content when transitioning from collapsed -> expanded', () => {
    const wrapper = mount(
      <SlideyPanel>
        <p>
          hi
        </p>
      </SlideyPanel>
    );

    wrapper.setProps({ expanded: true });
    wrapper.update();
    expect(wrapper.find('p').exists()).toBeTruthy();
    expect(wrapper.text()).toBe('hi');
  });

  it('hides content when transitioning from expanded -> collapsed', () => {
    const wrapper = mount(
      <SlideyPanel>
        <p>
          hi
        </p>
      </SlideyPanel>
    );

    wrapper.setProps({ expanded: false });
    wrapper.update();
    expect(wrapper.find('p').exists()).toBeFalsy();
  });

  it('slides down when expanded', () => {
    const wrapper = mount(
      <SlideyPanel $={fake$}>
        <p>
          hi
        </p>
      </SlideyPanel>
    );

    wrapper.setProps({ expanded: true });
    wrapper.update();
    expect(fake$.log).toEqual([
      'hide <span>',
      'slideDown <span> fast',
    ]);
  });

  it('slides up when collapsed', () => {
    const wrapper = mount(
      <SlideyPanel $={fake$}>
        <p>
          hi
        </p>
      </SlideyPanel>
    );

    wrapper.setProps({ expanded: true });
    wrapper.update();
    fake$.log = [];
    wrapper.setProps({ expanded: false });
    wrapper.update();
    expect(fake$.log).toEqual([
      'slideUp <span> fast',
    ]);
  });
});
