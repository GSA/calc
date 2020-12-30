# Change log

All notable changes to this project will be documented in this file,
which uses the format described in
[keepachangelog.com](http://keepachangelog.com/). This project adheres
to [Semantic Versioning](http://semver.org/).

## [Unreleased][unreleased]

## 2020-05-28

### Changed

- Repalced Price Prosal Template (PPT) for Mas consolidated contract vehicle


## 2020-05-04

### Changed

- Added additional(optional) search filters based on Sin mumber, Security Clearance 
- Upgraded snyk issues
- Addressed Bugs


## 2020-04-11

### Changed

- Added new search filter based on Keywords, Description, Certifications
- Added COVID-19 banner 
- Upgraded high and medium severity vulnerabilities (reported by snyk tool)


## 2020-03-18

### Changed

- More data clean up on data quality report
- Upgraded high and medium severity vulnerabilities (reported by snyk tool)


## 2020-02-25

### Changed

- Expired contracts and duplicated records were removed for the data quality report
- Upgraded 1 high severity on django (reported by snyk tool)


## 2020-01-27

### Changed

- Upgraded packages that is causing severity vulnerabilities.


## 2019-12-06

### Changed

- Fixes of Snyk 9 high severity and 5 medium severity vulnerabilities.

## 2019-11-19

### Changed

- Fix JavaScript issue of price list upload on Chrome browser.
- Add disclaimer on CALC under the Exact match box.
- Calc About page updates.

## 2019-11-19

### Changed

- Admin users has ability to upload Capability Statement file in CALC.
- Admin users has ability to add URL of a capability statement in CALC.
- Created API to get Capability statements. Any application can use this service to retriever capability statements by contact number.
- GSA API Standards Adoption for CALC.

## 2019-08-22

### Changed

- Performed FISMA Annual Self-Assessment CALC.


## 2019-10-08

### Changed

- Added Option to Upload the MAS Consolidation Pricing Template. (#2360)
- 1 high severity issues fixed (Reported by Synk tool).


## 2019-08-20

### Changed

- Update content on “about CALC” page. (#2317)
- What does CALC do?
- How can CALC help me?
- Where do the prices in this tool come from?
- Explanation of +/-1 standard deviation under CALC’s visualization

## 2019-07-12

### Added
- Price list upload feature for Schedule 71IIK. (#2310)

## 2019-07-03

### Changed
- 1 high severity issue fixed (Reported by Synk tool. Upgraded Django version to 1.11.21). (#2303)

## 2019-06-25

### Changed
- 2 high severity issues fixed (Reported by Synk tool). (#2300)

## 2019-06-20

### Added
- Implement Session Timeout For Admin Users. (#2298)

## 2019-05-23

### Changed
- 1 high severity issue fixed (Reported by Synk tool). (#2284)

## 2019-05-16

### Changed
- Update Linux instances to cflinuxfs3 from cflinuxfs2. (#2281)

## 2019-04-30

### Changed
- 1 high severity issue fixed (Reported by Synk tool). (#2277)

## 2019-04-19

### Changed
- 3 high severity and 2 medium severity issues fixed (Reported by Synk tool). (#2275)

## 2019-04-04

### Changed
- Removed New Relic from Calc App. (#2267)

## 2019-03-29

### Changed
- Removed Beta Tag from master. (#2264)

## 2019-03-07

### Changed
- 1 high severity issue fixed (Reported by Synk tool). (#2262)

## 2019-02-22

### Changed
- RQ Scheduler Version Upgrade. (#2260)

## 2019-02-08

### Changed
- 6 security issues fixed (Reported by Synk tool). (#2262)

## [3.2.2][] - 2018-09-28

### Changed
- Add NLTK's Averaged Perceptron Tagger `.pickle` file to repository instead of
  downloading it on every build, and make changes to build files and to price
  analysis reflecting those changes. (#2194)

## [3.2.1][] - 2018-09-27

### Added
- Add deployment step of NLTK resources to support price list analysis feature. (#2192)

### Changed
- Fixed a bug in lists of labor categories that are too long for proper visual display. (#2191)

## [3.2.0][] - 2018-09-27

### Added
- Schedule 70 contracting officers with login credentials can now have CALC
  analyze price lists and provide summary stats about them. (#997)
- The data upload process now has an overview and walkthrough of the process
  on the first page. (#1460)

### Changed
- Fixed a bug that caused CircleCI to time out on Jest tests. (#2149, #2155)
- Moved the data explorer's proposed price entry box down to be with the
  rest of the pricing summary numbers. (#2178)
- Changed the data explorer's summary hierarchy (#2178)
- Updated the design of the data explorer graph to match site colors. (#2143)
- Made some updates and language changes to the deployment documentation. (#2139)
- Removed some unused template tags from the header in the admin section that
  were rendering oddly. (#2162)
- Fixed a bug that made the "exact match" checkbox too wide. (#2141)

## [3.1.0][] - 2018-09-19

### Added
- Users can now search by vendor name or contract number in addition to labor category (#2069).
- The data upload tool now accepts Schedule 736 uploads (#2140).

## [3.0.1][] - 2018-09-04

### Changed
- Vendor name and contract number have been consolidated into a single column for easier scanning (#2112).
- Schedule selector search UI has been relocated and improved (#2085).
- Data administrators can now access the admin panel from the user menu rather than the main navigation (#2105).
- Search type UI has been simplified to a single checkbox (#2108).

### Added
- API documentation is now available in the CALC footer (#2065).

## [3.0.0][] - 2018-08-20

### Changed
- Changes to the options available for search. `match_phrase` has been removed as an
option due to observed limited utility and bugginess in the implementation. Any API
calls to `query_type` relying on `match_phrase` will return `match_words` results instead. The
`match_words` and `match_exact` options have also been refactored to remove outstanding bugs. (#2061)
- Updated UI to reflect search API changes (#2090).
- Fixed an issue with front end files not being built properly (#2088).
- Labelling across the site now reflects the potential availability of multiple
contract vehicles, not just schedules (#2067).
- Contract year buttons now have an explanatory tooltip ((#2056).

## [2.10.0][] - 2018-07-23

### Added
- Made it possible for data administrators to edit and add schedule names, descriptions, and SIN numbers, by centralizing schedule metadata in an API call (#2018).
- Added OpenGraph metadata tags (#2033).
- Added progressive enhancement to HTML5 form validation, allowing a standard error alert design (#2021).

### Changed
- Updated deployment docs (#2016) and styleguide docs (#2008).
- Updated styling for data capture stepper widget (#2015).
- Updated the visual design of the results table (#2027).
- Updated the visual design of alerts (#2017).
- Upgraded the version of `document-register-element` used by our web components (#2006).
- Updated the version of ESLint (#2048).
- Updated the version of gulp (#2044).


## [2.9.1][] - 2018-06-15

### Added

- Added developer documentation for linting, type checking, and editor
  integration (#1992).
- Added title to search page (#1988).

### Changed

- The `load_api_data` management command now updates search indices
  properly (#1987).
- Updated `django-uswds-forms` version and made it installable from
  PyPI (#1999).
- Fixed a bug in the way IE 11 reports certain events to Google
  Analytics (#2007).

### Removed

- CALC no longer has a `staging` deployment (#1795).


## [2.9.0][] - 2018-05-31

### Added

- The administrative UI now has introductory documentation,
  which will make it easier for new staff to onboard (#1844).
- A data quality report has been added at `/data-quality-report/`,
  which makes it easier to get an idea of how healthy CALC's
  data is (#1875).
- On local development instances, a "switch user" menu has
  been added to the top-right of every page, and sample users
  have been added, which makes it easier to see how the site
  looks and functions depending on the kind of user that is
  logged in (#1859).
- A `load_api_data` management command has been added, which
  makes it easy to "mirror" production CALC data on one's
  local instance (#1734). This obviated the need for the
  `load_data` and `load_s70` commands, so they were removed (#1774).
- CALC now uses react-loadable to load different UI components
  in separate bundles, which improves page load time. A
  Webpack bundle analyzer has also been added to make it
  easier to introspect the composition of our bundles.
  Documentation can be found in the "Analyzing bundles"
  section of the developer documentation's front end guide (#1736).

### Changed

- CALC now has a revamped logo and look-and-feel! We think it's awesome.
- The new CALC look-and-feel has been documented in the styleguide.
- Clicking anywhere outside of the user menu now closes it (#1804).
- CALC no longer uses api.data.gov to access its own API in
  production. Because of this, the `API_HOST` and `WHITELISTED_IPS`
  settings have been removed (#1766).
- A number of changes have been made to CALC's CSS:
    - CALC now uses the US Web Design System; it was formerly using
      bits and pieces of it that we had copy-and-pasted from USWDS.
      For more details on how we override USWDS and define our own
      custom variables, see the front-end developer guide.
    - CALC now uses USWDS's `usa-sr-only` class for screenreader-only
      content instead of `sr-only` (#1958).
    - CALC no longer uses words like "primary" and "secondary" in its
      SASS color names, instead opting for the actual names of the
      colors, such as `color-blue-darker` and `color-green-bright` (#1947).
- A number of changes have been made to the project's use of
  Google Analytics (GA):
    - Clicks on the "download graph" button in the Data Explorer are now
      tracked by GA (#1706).
    - Both Google Analytics accounts (DAP and standard GA) now
      behave in almost exactly the same ways, which should
      reduce confusion (#1852, #1853).
    - DAP is no longer used when users are authenticated (#1843).
- The developer documentation has been updated in a
  number of ways (#1698). In particular:
    - The Docker way of developing is now the default and _only_
      documented way of doing things. In other words, we no
      longer document how to get CALC up and running without
      Docker (#1793).
    - Docker troubleshooting documentation is now significantly
      more helpful (#1904).
    - API documentation has been moved to `/api/docs/`. It is now
      interactive (that is, users can enter search criteria and
      see the response returned by the server). It is auto-generated
      by Django REST Framework, which has been upgraded to
      3.8.2 (#1797, #1811, #1870, #1893).
    - A documentation section on analytics has been added (#1857).
- More source code has been documented and refactored for
  readability/maintainability. In particular:
    - Data capture schedule code has been documented and type-annotated (#1826).
    - The `Contract` model is now documented (#1850).
    - The project's CSS is now documented (#1871).
- Issue/PR numbers in the `/updates/` page are now automatically
  linked to their corresponding pages on GitHub (#1816).
- Searching for users in the admin panel works again (#1794).
- Upgraded React to 16 (#1685).
- Upgraded Babel, Webpack, and Node (#1687).
- Upgraded gulp-sass (#1785).
- Upgraded flake8/pyflakes (#1790).
- The usage of eslint has been rolled back to be less
  aggressive (#1852, #1867, #1868).
- API requests now validate the `sort` field properly to provide
  better feedback and mitigate DoS attacks (#1869).
- CALC's Selenium tests now use headless Chrome instead of
  PhantomJS, in both Docker and CircleCI (#1767).
- The Docker setup of CALC has been modified to limit container
  memory to their cloud.gov settings, ensuring better
  dev/prod parity (#1809).
- mypy is now run on all files, rather than a whitelist (#1815).
- All non-historic references to `hourglass` have been changed to
  `calc` (#1845).
- Upgraded d3-timer (#1977).

### Removed

- The `Contract` model's `piid` field has been removed, as it
  wasn't being used (#1935).

## [2.8.6][] - 2018-04-06

### Changed

- Fixed bulk upload to use less memory (#1714).

## [2.8.5][] - 2018-03-29

### Changed

- Improved performance of Region 10 bulk data upload processing (#1675).
- Switched to native PostgreSQL full-text search instead of using djorm-exp-pgfulltext (#1652).
- Upgraded to Django 1.11 (#1640).
- Upgraded to Redis 3.2 (#1647).
- Upgraded to React 15.5 (#1680).
- Upgraded dj-email-url in support of switching to Amazon SES for email sending (#1678).
- Fixed automated deployments to redeploy the main app and worker apps (#1651).
- Added coverage reporting for the Data Explorer React app (#1653).
- Setup nightly tests to be run against the production instance of CALC (#1654).
- Minimized vendor JavaScript bundle (#1655).

## [2.8.4][] - 2018-03-20

### Changed

- Use the latest version of Python 3.6.x in deployed applications (#1631).
- Fixed a bug that impacted the sending of emails from worker applications (#1599).
- Updated Code Climate config to match that services new format (#1629).
- Updated README with information about waiting for automated deploys to finish (#1598).

## [2.8.3][] - 2017-10-05

### Changed

- Fixed a bug whereby some region 10 spreadsheets would cause CALC bulk
  upload to fail (#1594).

## [2.8.2][] - 2017-10-03

### Changed

- The session cookie now expires when the user's browser is closed (#1584).
- All admin routes have the 'Cache-Control: no-cache' header to prevent browser caching (#1590).

## [2.8.1][] - 2017-10-02

### Changed

- The cross-origin security policy of the API has been hardened to
  only allow CORS requests under `/api/`, and only allow the
  `GET` and `OPTIONS` HTTP methods (#1585).

- Improved logging for price list status changes (#1579).

## [2.8.0][] - 2017-09-19

### Added

- Added additional required logging (#1569).

## [2.7.2][] - 2017-09-19

### Changed

- Switch to 3-tiered branch-based deployments (`develop`, `staging`, `master`).

## [2.7.1][] - 2017-09-19

### Changed

- Migrate from TravisCI to CircleCI.
- Upgrade to Python 3.6.2.
- Fix an issue that allowed CSVs exported from the Data Explorer to contain
  auto-running Excel formulas in the query field.

## [2.7.0][] - 2017-04-14

### Changed

- Upgraded Django to 1.9.3 (#1526).
- Upgraded jQuery to 3.2.1 (#1539).
- CALC is now prepared for migration to Django 1.10 (#1544). However,
  as the development team currently has a limited amount of time to
  work on CALC, we've decided not to actually migrate to the new
  version of Django, as we may not have time to address any problems
  occurring from the upgrade in the near future.

### Added

- Added support for recording and replaying attempted price list
  submissions (#1491), and added a new **Technical Support Specialist**
  role. This will allow the development team to better serve
  users who are having problems submitting their price lists.
- Added integration with Slack, so that the development team will be
  notified of events happening on CALC and be able to respond quickly
  to anything that needs attention (#1505).
- Added documentation on monitoring CALC (#1518).

## [2.6.0][] - 2017-03-24

### Changed

- Modified how autocomplete search results are returned from the server
  to improve the speed of retrieving, processing, showing results.
- Changed `/healthcheck/` to include an `is_everything_ok` property and
  always return `200` in order to effectively monitor that endpoint (#1516).
- Optimized client JavaScript by removing global D3, using Webpack to make
  all bundles, and switching to a React-based component for the Experience
  slider.

## [2.5.1][] - 2017-03-20

### Changed

- Fixed a bug that caused errors in the API due to a bad interaction between
  the New Relic monitor and djorm-ext-pgfulltext (#1498).

## [2.5.0][] - 2017-03-16

### Changed

- Fixed a bug in the data explorer search input that prevented searches for
  numeric strings (#1475).
- Fixed a bug in the the data explorer search input that would cause a
  JavaScript error when empty results were returned from the autocompletion
  API (#1484).
- Fixed a bug preventing Unit of Issue cells with extra spaces from passing
  validation (#1494).
- Modified the Schedule 70 price list parser to look for some variations on
  column names in order to accept more price list uploads.
- Fixed some minor styling bugs in the admin interface (#1326 and #1262).
- Upgraded CALC to use Django 1.9.

## [2.4.0][] - 2017-03-10

### Added

- When logged-in, the username in the upper right corner of the page has been
  turned into a small dropdown menu (#1413).

### Changed

- CALC now understands certain acronyms and abbreviations, such as
  "jr" (junior), "sr" (senior), and "sme" (subject matter expert). Searches
  for any of these will yield more inclusive results than before (#1378).
- System-generated emails have vastly improved styling (#1208).
- The logic to parse the minimum experience values from
  uploaded Schedule 70 price lists has been made more flexible by using the
  first numeric value encountered.
- The data explorer page now changes the page title based on the current search
  term(s) (#1315).
- Price list details pages have improved status indication styling (#980).
- Styling of the error page of the price list upload process has been improved
  (#1266).
- The Rates API now handles quotation-delimited search terms, like
  "engineer, senior" (#1459).

## [2.3.0][] - 2017-02-22

### Added

- CALC's developer documentation has been modularized and is now available at
  at `/docs/` (#1301).

### Changed

- A bug in the labor category search box that could cause the user's browser
  to lock up on special-character-only search queries has been fixed (#1355).

- The labor category search box and associated URL parameter now enforce a
  a maximum length of 255 characters (#1354).

- The navigation tabs no longer "jump" while the front page is loaded (#1341).

- Table header styling throughout CALC has been improved and made more
  consistent (#1202).

- Some minor styling bugs (#1229) and inconsistencies (#1371) in the filter box
  on the front have been corrected.

- CALC now runs on Python 3.6.0.

## [2.2.0][] - 2017-02-07

### Added

- A test suite for testing the production instance of CALC has been created
  (#1199).

### Changed

- The Schedule 70 price list parsing logic has been amended to address a bug
  where it attempted to parse rows outside of the price list table (#1318).

- Ethnio (used for recruiting users for research sessions) has been removed.

- The cloud.gov UAA authentication code has been extracted to a separate
  package called [`cg-django-uaa`](https://github.com/18F/cg-django-uaa).

- Most Python dependencies have been updated.

## [2.1.0][] - 2017-01-31

### Added

- A link to "Read about recent updates to CALC" now appears in the
  footer of every page.

### Changed

- Search queries ending with trailing commas and using the "contains phrase"
  criteria now work properly.

- CALC now validates minimum wages based on the value of $10.20 per
  hour, as set forth by
  [Executive Order 13658](https://www.dol.gov/whd/flsa/eo13658/index.htm).

- Various improvements to the copy of emails sent out by CALC have been
  made, thanks to the efforts of the 18F Writing Lab.

- Emails are also sent in HTML format (in addition to plain text) and
  include relevant links back to CALC where applicable.

- Sent emails also now have a `reply-to` header set to a valid email
  address that will be checked and responded-to by a CALC team member.

- Errors in uploaded price lists are now displayed via tooltips (#1245).

- Explicit HTTP `Cache-Control` headers are now set on responses so that
  Amazon CloudFront will behave properly when new versions of CALC are
  deployed.

- A new `manage.py send_example_emails` command has been added to make
  it easier to iterate on the emails sent by CALC.

## [2.0.0][] - 2017-01-18

### Added

- The new data capture functionality has been added, allowing COs
  to log in (via cloud.gov) and submit their approved Schedule 70
  price lists. Data administrators can then review these price lists and
  add their data into CALC.

- Additionally, data administrators can directly upload Region 10
  bulk data. The uploaded data will then replace all existing Region 10
  data in CALC.

### Changed

- In October 2015, the schedules represented in CALC were consolidated
  into the [Professional Services Schedule][pss] to give federal agency
  acquisition professionals the ability to obtain total contract solutions
  for their professional services requirements using one contract vehicle.

  Consequently, the "Schedule" filter in the data explorer has
  been renamed to the "SIN / Schedule" filter, and allows rates to be
  filtered by SIN number.

- Searching for multiple words in the data explorer's search field
  now produces expected autocompletion results.

- The data explorer is now much more keyboard-accessible and
  screenreader-friendly.

- The "proposed price" field in the data explorer automatically
  updates the histogram on a per-keypress basis; there is no longer
  any need to click the "Go" button.

- Sharing CALC links with the "Education" field filled out now works
  properly.

- The CALC banner has been redesigned to be less confusing and easier
  to read.

- Google Analytics for CALC now properly track new searches in the
  data explorer as page views. We also track clicks on links in the
  "Contract #" column of the data explorer results table.

[pss]: https://www.gsa.gov/portal/content/246403

## [1.2.0][] - 2015-07-21

- filtering empty list items out of query building

## [1.1.2][] - 2015-07-14

- Merge pull request #224 from 18F/ethnio
- Add ethnio screener

## [1.1.1][] - 2015-07-08

- hide proposed price field so that we may deploy to production
  everything but this feature

## [1.1.0][] - 2015-07-07

- Merge pull request #211 from 18F/add-histogram-design
- Updates to histogram

## [1.0.1][] - 2015-06-29

- Merge pull request #205 from 18F/search-bug
- Strip non-alpha numeric or whitespace chars out of search query

## 1.0.0 - 2015-06-24

- adds hidden proposed price starting functionality
- adds standard deviation callouts
- adds icons in header
- workflow documentation
- bug fix for stacked histogram labels
- removing python 2.7 support
- script to run django migrations on cloud foundry
- slider and drop downs to replace single drop down for years experience
- refining header wording
- replace drop down for education with multi select

[unreleased]: https://github.com/18F/calc/compare/v3.2.2...HEAD
[3.2.2]: https://github.com/18F/calc/compare/v3.2.1...v3.2.2
[3.2.1]: https://github.com/18F/calc/compare/v3.2.0...v3.2.1
[3.2.0]: https://github.com/18F/calc/compare/v3.1.0...v3.2.0
[3.1.0]: https://github.com/18F/calc/compare/v3.0.1...v3.1.0
[3.0.1]: https://github.com/18F/calc/compare/v3.0.0...v3.0.1
[3.0.0]: https://github.com/18F/calc/compare/v2.10.0...v3.0.0
[2.10.0]: https://github.com/18F/calc/compare/v2.9.1...v2.10.0
[2.9.1]: https://github.com/18F/calc/compare/v2.9.0...v2.9.1
[2.9.0]: https://github.com/18F/calc/compare/v2.8.6...v2.9.0
[2.8.6]: https://github.com/18F/calc/compare/v2.8.5...v2.8.6
[2.8.5]: https://github.com/18F/calc/compare/v2.8.4...v2.8.5
[2.8.4]: https://github.com/18F/calc/compare/v2.8.3...v2.8.4
[2.8.3]: https://github.com/18F/calc/compare/v2.8.2...v2.8.3
[2.8.2]: https://github.com/18F/calc/compare/v2.8.1...v2.8.2
[2.8.1]: https://github.com/18F/calc/compare/v2.8.0...v2.8.1
[2.8.0]: https://github.com/18F/calc/compare/v2.7.2...v2.8.0
[2.7.2]: https://github.com/18F/calc/compare/v2.7.1...v2.7.2
[2.7.1]: https://github.com/18F/calc/compare/v2.7.0...v2.7.1
[2.7.0]: https://github.com/18F/calc/compare/v2.6.0...v2.7.0
[2.6.0]: https://github.com/18F/calc/compare/v2.5.1...v2.6.0
[2.5.1]: https://github.com/18F/calc/compare/v2.5.0...v2.5.1
[2.5.0]: https://github.com/18F/calc/compare/v2.4.0...v2.5.0
[2.4.0]: https://github.com/18F/calc/compare/v2.3.0...v2.4.0
[2.3.0]: https://github.com/18F/calc/compare/v2.2.0...v2.3.0
[2.2.0]: https://github.com/18F/calc/compare/v2.1.0...v2.2.0
[2.1.0]: https://github.com/18F/calc/compare/v2.0.0...v2.1.0
[2.0.0]: https://github.com/18F/calc/compare/v1.2.0...v2.0.0
[1.2.0]: https://github.com/18F/calc/compare/v1.1.2...v1.2.0
[1.1.2]: https://github.com/18F/calc/compare/v1.1.1...v1.1.2
[1.1.1]: https://github.com/18F/calc/compare/v1.1.0...v1.1.1
[1.1.0]: https://github.com/18F/calc/compare/v1.0.1...v1.1.0
[1.0.1]: https://github.com/18F/calc/compare/v1.0.0...v1.0.1
