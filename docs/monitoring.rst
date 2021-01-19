==============
Monitoring
==============

### Healthcheck

CALC has an endpoint at `/healthcheck/` which always
returns a `200 OK` response of type `application/json`. The
returned object has the following keys:

* `version` is the version of CALC deployed, e.g. `'2.5.1'`.

* `canonical_url` is the absolute, canonical URL of the
  `/healthcheck/` endpoint based on Django's default
  `Site` object.

* `request_url` is the absolute URL of the `/healthcheck/`
  endpoint based on request headers.

* `canonical_url_matches_request_url` is a boolean
  indicating whether `canonical_url` is equal to
  `request_url`. If this is `false`, then the site is
  considered to be unhealthy.

* `rq_jobs` is the number of enqueued jobs waiting to be
  processed by the [redis queue (RQ)][rq].

* `is_database_synchronized` is a boolean indicating whether
  all migrations have been run on the database. If
  this is `false`, the site is considered to be unhealthy.

* `postgres_version` is the version of Postgres being used
  by the database.

* `is_everything_ok` is a boolean indicating whether the
  server as a whole is healthy. If any of the values
  described above indicate that the site is unhealthy, then
  the value of `is_everything_ok` will be `false`.

For more details on the `/healthcheck/` endpoint, see
[calc/healthcheck.py](../calc/healthcheck.py).

On production, we've also configured a [New Relic Synthetics][]
monitor to ping `/healthcheck/` on a regular basis, so that
administrators are notified if CALC is ever unhealthy.

### Production tests

CALC has a suite of tests in [production_tests](../production_tests/) for
checking that the production site is properly configured.

These tests are run nightly as a workflow build in CircleCI.

