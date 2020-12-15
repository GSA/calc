import toJson from 'enzyme-to-json';

import { ProposedPrice } from '../components/proposed-price';
import makeSetup from './testSetup';

const defaultProps = {
  proposedPrice: 120.49,
  setProposedPrice: jest.fn(),
  idPrefix: 'zzz_',
};

const setup = makeSetup(ProposedPrice, defaultProps);

describe('<ProposedPrice>', () => {
  it('renders correctly', () => {
    const { props, wrapper } = setup();
    expect(wrapper.find('.proposed-price').exists()).toBeTruthy();
    const input = wrapper.find('input#zzz_proposed-price');
    expect(input.exists()).toBeTruthy();
    expect(input.prop('value')).toBe(props.proposedPrice);
  });

  it('matches snapshot', () => {
    const { wrapper } = setup();
    expect(toJson(wrapper)).toMatchSnapshot();
  });

  it('calls setProposedPrice on change', () => {
    const { props, mounted } = setup();
    const input = mounted.find('input#zzz_proposed-price');
    input.simulate('change', { target: { value: '140.22' } });
    expect(props.setProposedPrice.mock.calls.length).toBe(1);
    expect(props.setProposedPrice.mock.calls[0][0]).toBe(140.22);
  });

  it('calls setProposedPrice with 0 on non-float input', () => {
    const { props, mounted } = setup({ setProposedPrice: jest.fn() });
    const input = mounted.find('input#zzz_proposed-price');
    input.simulate('change', { target: { value: 'abc' } });
    expect(props.setProposedPrice.mock.calls.length).toBe(1);
    expect(props.setProposedPrice.mock.calls[0][0]).toBe(0);
  });
});
