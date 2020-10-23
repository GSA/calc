'use strict';

require('dotenv').config({ silent: true });

if (!('DEBUG' in process.env)) {
  process.env.NODE_ENV = 'production';
}

const { spawn } = require('child_process');
const path = require('path');

const gulp = require('gulp');
const sass = require('gulp-sass');
const cleancss = require('gulp-clean-css');
const concat = require('gulp-concat');
const sourcemaps = require('gulp-sourcemaps');
const rename = require('gulp-rename');
const gutil = require('gulp-util');
const del = require('del');
const uglify = require('gulp-uglify');
const gulpif = require('gulp-if');
const bourbonNeatPaths = require('bourbon-neat').includePaths;
const named = require('vinyl-named');

const webpackUtil = require('./frontend/gulp/webpack-util');

const USWDS_DIST = 'node_modules/uswds/dist';

const BUILT_FRONTEND_DIR = 'frontend/static/frontend/built';

const isProd = process.env.NODE_ENV === 'production';
gutil.log(`Gulp is running in ${isProd ? 'production' : 'development'} mode`);

const dirs = {
  src: {
    style: 'frontend/source/sass/',
    scripts: 'frontend/source/js/',
    sphinx: 'docs/',
  },
  dest: {
    style: {
      built: `${BUILT_FRONTEND_DIR}/style`,
    },
    scripts: {},
  },
};

const paths = {
  sass: '**/*.scss',
  js: '**/*.@(js|jsx)',
  sphinx: '*.@(md|py|rst)',
};

const bundles = {
  // Scripts common to Data Explorer and Data Capture
  common: {},
  // Data Explorer scripts
  dataExplorer: {
    dirName: 'data-explorer',
    vendor: [
      'vendor/rgbcolor.js',
      'vendor/StackBlur.js',
      'vendor/canvg.js',
      'vendor/canvas-toBlob.js',
      'vendor/FileSaver.js',
      'vendor/jquery.auto-complete.js',
    ],
  },
  // Data Capture scripts
  dataCapture: {
    dirName: 'data-capture',
  },
  // Styleguide scripts
  styleguide: {},
  // Test scripts
  tests: {},
};

function concatAndMapSources(name, sources, dest) {
  return gulp.src(sources)
    .pipe(sourcemaps.init())
    .pipe(concat(name))
    .pipe(gulpif(isProd, uglify()))
    .pipe(sourcemaps.write('./'))
    .pipe(gulp.dest(dest));
}

const vendoredBundles = [];

// Generate tasks for all the vendor bundles
Object.keys(bundles).forEach((name) => {
  const options = bundles[name];
  const dirName = options.dirName || name;
  const vendor = options.vendor || [];

  if (vendor.length) {
    const vendoredBundleName = `js:${dirName}:vendor`;
    gulp.task(
      vendoredBundleName, () => concatAndMapSources( // eslint-disable-line no-use-before-define
        `${dirName}.vendor.js`,
        vendor.map(p => dirs.src.scripts + p),
        `${BUILT_FRONTEND_DIR}/js/`
      )
    );

    vendoredBundles.push(vendoredBundleName);
  }
});

gulp.task('sphinx', (cb) => {
  const sphinx = spawn('make', ['html'], {
    stdio: 'inherit',
    cwd: path.join(__dirname, '/docs'),
    shell: true,
  });
  sphinx.on('exit', (code) => {
    if (code !== 0) {
      cb(new Error('Sphinx failed!'));
      return;
    }
    cb(null);
  });
});

gulp.task('copy-uswds-assets', () => gulp.src(`${USWDS_DIST}/@(js|fonts|img)/**/**`)
  .pipe(gulp.dest(`${BUILT_FRONTEND_DIR}/vendor/uswds/`)));

gulp.task('clean', () => {
  function getPaths(obj) {
    return Object.keys(obj).map(k => path.join(obj[k], '**/*'));
  }

  const styleDirs = getPaths(dirs.dest.style);
  const scriptDirs = getPaths(dirs.dest.scripts);

  del([].concat(styleDirs, scriptDirs));
});

// boolean flag to indicate to webpack that it should set up its watching
let taskNum = 1; // eslint-disable-line prefer-const
let isWatching = false;
gulp.task('set-watching', (done) => {
  isWatching = true;
  done();
});

// compile SASS sources
gulp.task('sass', () => gulp.src(path.join(dirs.src.style, paths.sass))
  .pipe(sourcemaps.init())
  .pipe(sass({
    includePaths: [bourbonNeatPaths, 'node_modules'],
  })
    .on('error', sass.logError)
    .on('error', () => {
      // When running a production build, break the stream
      // if there is an error so that the build fails.
      if (!isWatching) { throw new Error('Errors in SASS build.'); }
    }))
  .pipe(rename({ suffix: '.min' }))
  .pipe(cleancss())
  .pipe(sourcemaps.write('./'))
  .pipe(gulp.dest(dirs.dest.style.built)));

gulp.task('js:vendor', gulp.series(vendoredBundles));

gulp.task('js:webpack', done => gulp.src(
  webpackUtil.scriptSources({ bundles, rootDir: dirs.src.scripts })
)
  .pipe(named(webpackUtil.getLastFolderName))
  .pipe(webpackUtil.webpackify({ isWatching, isProd }, done, taskNum))
  .pipe(gulp.dest(`${BUILT_FRONTEND_DIR}/js/`)));

// Compile JavaScript sources
gulp.task('js', gulp.parallel('js:vendor', 'js:webpack'));

// production build task
// will need to run before collectstatic
// `yarn gulp build` or `gulp run build` if gulp-cli is installed globally
gulp.task('build', gulp.series('copy-uswds-assets', 'sass', 'js', 'sphinx'));

// watch files for changes
gulp.task('watch', gulp.series('set-watching', gulp.parallel('copy-uswds-assets', 'sass', 'js', 'sphinx'), () => {
  gulp.watch([
    path.join(dirs.src.sphinx, paths.sphinx),
  ], gulp.series('sphinx'));
  gulp.watch(path.join(dirs.src.style, paths.sass), gulp.series('sass'));

  // Note: wepback bundles set up their own watch handling
  // so we don't want to re-trigger them here, ref #437
  gulp.watch(path.join(dirs.src.scripts, 'vendor', paths.js), gulp.series('js:vendor'));

  const calcURL = `http://localhost:${process.env.DOCKER_EXPOSED_PORT}`;

  gutil.log("-----------------------------------------");
  gutil.log(`Visit your CALC at: ${calcURL}`);
  gutil.log("-----------------------------------------");
}));

// default task
// running `gulp` will default to watching and dist'ing files
// gulp.task('default', ['watch']);
gulp.task('default', gulp.series('watch'));

// set up a SIGTERM handler for quick graceful exit from docker
process.on('SIGTERM', () => {
  process.exit(1);
});
