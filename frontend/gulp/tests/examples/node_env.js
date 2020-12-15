global.myNodeEnv = process.env.NODE_ENV;

if (process.env.NODE_ENV === 'production') {
  global.log = 'I AM PRODUCTION';
} else {
  global.log = 'I AM NOT PRODUCTION';
}
