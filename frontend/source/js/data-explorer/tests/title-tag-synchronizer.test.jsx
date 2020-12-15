import { TitleTagSynchronizer } from '../components/title-tag-synchronizer';
import makeSetup from './testSetup';

describe('<TitleTagSynchronizer>', () => {
  let fakeDocument;
  let wrapper;

  const setup = (extraProps) => {
    fakeDocument = Object.assign({}, { title: 'original' });

    const defaultProps = {
      q: '',
      document: fakeDocument,
    };

    wrapper = makeSetup(/* eslint-disable-line prefer-destructuring */
      TitleTagSynchronizer,
      defaultProps,
      { wrapperOnly: true }
    )(extraProps).wrapper;
  };

  it('leaves title unchanged on mount if query is empty', () => {
    setup();
    expect(fakeDocument.title).toEqual('original');
  });

  it('sets title to search query on mount if it is non-empty', () => {
    setup({ q: 'blarg' });
    expect(fakeDocument.title).toEqual('blarg - CALC Search');
  });

  it('sets title to non-empty search query on props change', () => {
    setup();
    wrapper.setProps({ q: 'boop,' });
    expect(fakeDocument.title).toEqual('boop - CALC Search');
  });

  it('sets title to original if query is empty on props change', () => {
    // TODO: fix
    setup({ q: 'boop' });
    wrapper.setProps({ q: '' });
    wrapper.update();
    expect(fakeDocument.title).toEqual('original');
  });

  it('resets title to original on unmount', () => {
    // TODO: fix
    setup({ q: 'boop' });
    wrapper.unmount();
    expect(fakeDocument.title).toEqual('original');
  });
});
