## Release process

This documents the process for issuing and deploying a new
release for CALC.

These docs walk through the process of creating release `0.0.4`.
You can simply replace this value for your own, or
run `docker-compose run app python manage.py releasehelp` to generate a
customized version of these instructions for the version number you're releasing.
(CALC follows [semantic versioning][semver], and you can tell what version it's
currently on by looking at the [CHANGELOG][changelog].)

**Note:** When following these instructions, ensure that no one else is
merging any PRs into `develop`; at the time of this writing, cloud.gov will
run out of memory quota if multiple branches of CALC are deployed
simultaneously!

To release version 0.0.4 of CALC:

1.  Create a branch off `develop` called `v0.0.4-rc` and push it to
    GitHub:

    ```
    git checkout -b v0.0.4-rc develop
    git push -u git@github.com:18F/calc.git v0.0.4-rc
    ```

2.  As you've worked on CALC through the last sprint, you should have updated the
    ["Unreleased" section of `CHANGELOG.md`][unreleased] with major features,
    bug fixes, and pull requests. Now, you'll want to verify that it is
    up-to-date by comparing it against GitHub's [commit list][commitlist],
    and then describing the changes in a human-meaningful form (see previous
    release entries for the appropriate level of human-friendliness).

    Feel free to move more important, less technical entries to the top
    of the list. Remember, it will be read by both developers *and* users,
    so avoid the use of jargon where possible.

    If you've changed anything in `CHANGELOG.md`, go ahead and commit it now:

    ```
    git add CHANGELOG.md
    git commit -m "Updated changelog."
    git push
    ```

3.  [Issue a PR][pr] to merge your branch into `master` titled
    "Tag and release v0.0.4 to production". Paste in the latest changes from the
    topmost "Unreleased" section of `CHANGELOG.md` into the
    description of the PR so stakeholders know what's changed. If you're
    on OS X, you can easily copy this to your clipboard with the following
    command:

    ```
    docker-compose run app python manage.py unreleased_changelog | pbcopy
    ```

4.  Wait for the stakeholders to sign-off on the release if there are
    functional or product changes, but **do not merge the PR yet**.
    The release candidate has just been approved to become the new
    release, so you'll need one more commit to make it official.

5.  Update the version number in `calc/version.py` to `0.0.4` and then
    run:

    ```
    docker-compose run app python manage.py bump_changelog
    ```

    This will create a new entry for the new version in `CHANGELOG.md`,
    and it will also output your new version's release notes to
    `tag-message-v0.0.4.txt`.

6.  Commit the changes to git and push them:

    ```
    git commit -a -m "Release v0.0.4."
    git push
    ```

7.  Make sure that all automated QA services (CircleCI, etc) think
    the PR looks good.

8.  Merge the PR into `master` via the **Create a merge commit** merge
    strategy (i.e., do *not* squash or rebase). Once [CircleCI][] is finished,
    the site will be deployed to [production][production].

9.  Visit the [production instance][production] and make sure all is functioning as
    expected.

10. Tag the release and push it, so that the release shows up in
    the project's [releases][] page:

    ```
    git tag -a v0.0.4 -F tag-message-v0.0.4.txt
    git push origin v0.0.4
    ```

11. Merge `master` back into `develop` on the remote repository:

    ```
    git fetch
    git checkout develop
    git pull https://github.com/18F/calc.git develop
    git merge origin/master
    git push https://github.com/18F/calc.git develop
    ```

Hooray, you're done!

[semver]: https://semver.org/
[changelog]: https://github.com/18F/calc/blob/develop/CHANGELOG.md
[commitlist]: https://github.com/18F/calc/commits/develop
[unreleased]: https://github.com/18F/calc/blob/develop/CHANGELOG.md#unreleased
[pr]: https://github.com/18F/calc/compare/master...v0.0.4-rc
[production]: https://calc.gsa.gov
[CircleCI]: https://circleci.com/gh/18F/calc
[releases]: https://github.com/18F/calc/releases
