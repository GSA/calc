## Continuous integration

CALC uses a number of third-party services to ensure consistent code quality.

### CircleCI

[CircleCI][] ensures that, when CALC's codebase changes, all tests still pass.
Its configuration is stored in [.circleci/config.yml][].

Aside from running tests, CircleCI is also used to automatically deploy
CALC; see the [Release process](release.md) documentation for further
details.

Finally, CircleCI is also used for some [monitoring](monitoring.md) tasks.

#### Disabling tests

Because a single failing test on CircleCI blocks deployment, it's important to
know how to disable some of them in emergencies. In particular:

* Selenium has a history of acting up on CI and sometimes needs
  to be disabled outright. See [commit 191f5789a8](https://github.com/18F/calc/commit/191f5789a8f477f493552ef9046baab0e4fb0c02)
  for an example of how to do this.

* CALC uses a number of static analysis tools to ensure that its
  code works as expected. However, in the case that any of them
  ever cause trouble whose causes can't be diagnosed, they can
  be disabled during CI: in [.circleci/config.yml][], search for
  `ultratest` and remove any of the arguments that are triggering
  failures.

### Code Climate

[Code Climate][] is used to ensure that CALC's code stays maintainable,
and that test coverage across our Python and JavaScript source
generally doesn't go down.

Its configuration is located in [.codeclimate.yml](../.codeclimate.yml).

Its checks are largely advisory, however. Sometimes false positives
are triggered and need to be silenced via its admin interface.

[CircleCI]: https://circleci.com/gh/18F/calc
[Code Climate]: https://codeclimate.com/github/18F/calc
[.circleci/config.yml]: ../.circleci/config.yml
