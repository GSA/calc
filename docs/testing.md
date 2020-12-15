## Testing

CALC provides a custom Django management command to run all linters and tests:

```sh
docker-compose run app python manage.py ultratest
```

### Python unit tests

To run just unit tests:

```sh
docker-compose run app py.test
```

For more information on running only specific tests, see
[`py.test` Usage and Invocations][pytest].

### Front end tests

For more details on front end testing, see the [front end guide](frontend.md).

### Integration tests

Some tests use Selenium/WebDriver with Chrome and [ChromeDriver][] to
ensure that the back-end and front-end integrate properly. The
following environment variables may be useful when configuring these
tests:

* `WD_CHROME_ARGS` are command-line flags to pass to Chrome,
  e.g. `--headless --no-sandbox --disable-setuid-sandbox`.

* `TEST_WITH_ROBOBROWSER` is a boolean that indicates whether to run
  some integration tests using [RoboBrowser][] instead of Selenium/WebDriver.
  Running tests with RoboBrowser can be much faster and less error-prone
  than via Selenium, but it also means that the tests are less end-to-end.

* `SKIP_STATIC_ASSET_BUILDING` is a boolean that indicates whether to
  skip the building of front-end static assets before running any
  integration tests. This can be useful if you need to fix a broken
  test that doesn't require changing any front-end assets.

[ChromeDriver]: https://sites.google.com/a/chromium.org/chromedriver/
[RoboBrowser]: http://robobrowser.readthedocs.io/

### Security scans

We use [bandit](https://github.com/openstack/bandit) for security-related
static analysis.

To run bandit:

```sh
docker-compose run app bandit -r .
```

bandit's configuration is in the [`.bandit`](../.bandit) file.

[pytest]: https://pytest.org/latest/usage.html
