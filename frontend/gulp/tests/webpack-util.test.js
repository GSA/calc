/**
 * @jest-environment node
 */

import path from 'path';
import vm from 'vm';
import gulp from 'gulp';

import webpackUtil from '../webpack-util';

describe('scriptSources', () => {
  it('uses bundle dirName when it is defined', () => {
    expect(webpackUtil.scriptSources({
      bundles: { foo: { dirName: 'bar' } },
      rootDir: '/js',
    })).toEqual(['/js/bar/index.js']);
  });

  it('uses bundle name when dirName is not defined', () => {
    expect(webpackUtil.scriptSources({
      bundles: { foo: {} },
      rootDir: '/js',
    })).toEqual(['/js/foo/index.js']);
  });
});

describe('getLastFolderName()', () => {
  it('works', () => {
    expect(webpackUtil.getLastFolderName({ path: '/a/b/c/bleh.js' }))
      .toEqual('c');
  });
});

function webpackify(filename, options = {}) {
  return new Promise((resolve) => {
    jest.setTimeout(100000);
    const src = gulp.src(path.join(__dirname, filename))
      .pipe(webpackUtil.webpackify(Object.assign({
        isWatching: false,
        isProd: false,
      }, options)));
    src.on('data', resolve);
  });
}

function execInVm(file) {
  const sandbox = {};
  const script = new vm.Script(file.contents.toString());
  const context = vm.createContext(sandbox);
  script.runInContext(context);
  return sandbox;
}

describe('webpackify', () => {
  it('sets __filename properly', () => webpackify('examples/filename.js').then((file) => {
    expect(execInVm(file).myFilename)
      .toEqual('frontend/gulp/tests/examples/filename.js');
  }));

  it('performs dead code removal in production', () => webpackify('examples/node_env.js', {
    isProd: true,
  }).then((file) => {
    const sandbox = execInVm(file);
    expect(sandbox.myNodeEnv).toEqual('production');
    expect(sandbox.log).toEqual('I AM PRODUCTION');
    expect(file.contents.toString())
      .not.toEqual(expect.stringMatching(/I AM NOT PRODUCTION/));
  }));

  it('sets NODE_ENV to empty string when not in production', () => webpackify('examples/node_env.js', {
    isProd: false,
  }).then((file) => {
    const sandbox = execInVm(file);
    expect(execInVm(file).myNodeEnv).toEqual('development');
    expect(sandbox.log).toEqual('I AM NOT PRODUCTION');
  }));
});
