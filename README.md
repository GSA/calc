# CALC overview

[CALC](https://calc.gsa.gov/) is a tool to help contracting personnel estimate their per-hour labor costs for a contract, based on historical pricing information. The tool is live at [https://calc.gsa.gov](https://calc.gsa.gov). You can track progress or file an issue on this repo; see our [contributor guidelines](CONTRIBUTING.md).

- [Current development status](#current-status)
- [Technical documentation](#technical-documentation)
    - [Developer documentation](#developer-documentation)
    - [API documentation](#api-documentation)
    - [Front end documentation](#front-end-documentation)
    - [System owner documentation](#system-owner-documentation)
    - [Team and task management documentation](#team-and-task-management-documentation)
- [CALC experiments](#calc-experiments)
- [Data Explorer](#data-explorer)
	- [Data Explorer history](#data-explorer-history)
- [How CALC helps procurement professionals](#how-calc-helps-procurement-professionals)
	- [Data Explorer usage by the numbers](#data-explorer-usage-by-the-numbers)
		- [CALC users from April 2017 to April 2018](#calc-users-from-april-2017-to-april-2018)
- [Data Capture](#data-capture)
	- [How Data Capture works](#how-data-capture-works)
- [Minor epiphanies along the way](#minor-epiphanies-along-the-way)
- [Addendum](#addendum)
	- [[Related 18F blog posts](https://18f.gsa.gov/tags/calc/)](#related-18f-blog-postshttps18fgsagovtagscalc)

## Current development status

[![CircleCI](https://circleci.com/gh/18F/calc.svg?style=svg)](https://circleci.com/gh/18F/calc)
[![Code Climate](https://codeclimate.com/github/18F/calc/badges/gpa.svg)](https://codeclimate.com/github/18F/calc)
[![Test Coverage](https://codeclimate.com/github/18F/calc/badges/coverage.svg)](https://codeclimate.com/github/18F/calc/coverage)
[![Dependency Status](https://snyk.io/test/github/18F/calc/badge.svg)](https://snyk.io/test/github/18F/calc)

## Technical documentation

To get started working on CALC, you'll probably want to start with
the [Docker setup guide](docs/docker.md).

The [CALC wiki](https://github.com/18F/calc/wiki) provides some context around
project history, how to orient yourself with the codebase, and how to do security reviews.

You may also find the following documents useful:

* [Change log](CHANGELOG.md)
* [Contributor guidelines](CONTRIBUTING.md)
* [License](LICENSE.md)


### Developer documentation

The most readable version of the project's developer documentation
can be found at
[calc-dev.app.cloud.gov/docs/](https://calc-dev.app.cloud.gov/docs/).

The developer documentation is
also available in this repository's [docs](docs/) directory.


### API documentation

To get started with the CALC APIs, you can jump straight to the 
[CALC API documentation](https://calc-dev.app.cloud.gov/api/)


### Front end documentation

We have a combined [style guide/component library](https://calc-dev.app.cloud.gov/styleguide/)
where we've documented things like site colors, form styles, page layout templates,
and our progressively enhanced widgets.


### System owner documentation

You may find it helpful to review our [guidelines on how to conduct
and document the weekly log and security event reviews.](https://github.com/18F/calc/wiki/Weekly-Log-and-Security-Event-Reviews)


### Team and task management documentation

The 18F CALC team managed sprints via [Zenhub](https://www.zenhub.com/) boards and epics.
Installing and using this extension might help clarify the relationship of some issues
to one another.

## CALC experiments

* [18F/calc-analysis](https://github.com/18F/calc-analysis) is a separate
  repository that contains data science experiments and other analyses that use CALC
  data.
* [Price prediction](https://github.com/18F/calc/pull/1562) was a feature explored
  with the intent of helping contracting officers make the best long-term decisions.
  Ultimately this was closed because of the difficulty of testing the accuracy of such a feature.
* [The CALC data dashboard](https://github.com/18F/calc/pull/1993) was a feature that gave
  users the ability to see a variety of stats about data in CALC, such as how recent it is.
  This was closed simply because the team had higher priorities, but could be easily explored in the future.
* [Changing the default data explorer dashboard](https://github.com/18F/calc/pull/1768) to show
  only the search box on load was a response to user confusion about what the graph and table
  show on page load. This idea could be explored further, but was closed because of lack
  of user testing.


## How CALC helps procurement professionals

During research with GSA Regions 2, 6, 10, and 11, we found contracting officers, contract specialists, and other GSA procurement professionals…

* who use CALC save roughly five hours per contract vs. GSA Advantage.

* who don't use CALC choose individual—often outlying—examples over aggregate data.

* have to somewhat blindly choose data points giving an incomplete view of awarded schedule rates.

* hop between many disparate systems cutting and pasting.

* want more data in CALC. (This was a major focus of work in 2016 and 2018.)

* are subject to contracting procedures and norms that vary wildly between regions and schedules.

## Data Explorer

The Data Explorer is how we refer to the front page of CALC, which is most commonly used by the public and by contracting professionals seeking to research labor rates. When someone says “CALC", this is probably the piece they are talking about.

### Data Explorer history

CALC was conceived by GSA Region 10's Kelly Bailey and created by 18F’ers during 2014 and 2015; none of them still work at 18F. A subsequent team did a lot of refactoring to the code in 2016 and 2018. It could definitely use some additional thinking / modifications, but wasn’t under the purview of the CALC 2016 or 2018 engagements.

### Data Explorer usage by the numbers

While the majority of CALC research, design, and development has been focused on usage by contracting professionals inside the GSA (specifically FAS regions 2, 6, 10, and 11), most CALC users come from outside.

#### CALC users from April 2017 to April 2018

Most CALC traffic came from domains controlled by an organization not accessible by the general public. Here's a breakdown of identifiable traffic:

| Organization | % of users | % of gov users |
| ------------ |-----------:| --------------:|
| private contractors | 29.2% | n/a |
| DoD | 25.4% | 33.3% |
| GSA | 8.7% | 11.5% |
| HHS | 5.7% | 7.5% |
| Energy | 4.6% | 6.0% |
| Interior | 3.7% | 4.9% |
| Transportation | 3.1% | 4.1% |
| independent agencies | 2.7% | 3.5% |
| VA | 2.6% | 3.5% |
| NASA | 2.1% | 2.7% |
| Commerce | 2.1% | 2.7% |
| Justice | 1.7% | 2.3% |
| Treasury | 1.4% | 1.9% |
| state government | 1.4% | n/a |
| Agriculture | 1.3% | 1.7% |
| State | 1.1% | 1.4% |
| county government | 0.8% | n/a |
| Labor | 0.5% | 0.7% |
| HUD | 0.5% | 0.6% |
| Education | 0.4% | 0.5% |
| private universities | 0.3% | n/a |
| EOP | 0.3% | 0.4% |
| Legislative Branch | 0.3% | 0.3% |
| Judiciary Branch | 0.1% | 0.1% |
| foreign governments | 0.1% | n/a |
| Homeland Security | 0.0% | 0.0% |

## Data Capture

Data Capture refers to the part of CALC built in 2016 and expanded in 2018. It provides a means for contracting officers to upload price lists into CALC.

### How Data Capture works

GSA acquisition professionals can add price lists directly to CALC after their schedule has been added to data-capture and they've been granted upload access by a CALC admin.You can see an overview of this process here (must be logged in): https://calc.gsa.gov/data-capture/tutorial

## Minor epiphanies along the way

* “Schedule” is the term for the tables of federally approved prices for labor categories. For instance, Schedule 70 contains most of the technology roles.
Schedules have perhaps been replaced by SIN (Special Item Number) groups?

  * From GSA Schedules FAQs:
  > “GSA Multiple Award Schedule (MAS) contracts, also referred to as GSA Schedule and Federal Supply Schedule contracts, are indefinite delivery, indefinite quantity (IDIQ) contracts that are available for use by federal agencies worldwide. … Under the MAS Program, GSA enters into governmentwide contracts with commercial firms to provide over 11 million commercial supplies and services. Agencies place orders directly with MAS contractors.”

  * Regions are not just geographic regions. In the world of FAS procurement, they are also responsible for managing whole categories of kinds of work that can be contracted-out to the federal government. For example, Region 10 is the home of professional services (white-collar jobs), while Region 6 is the home of more blue-collar work. (We did field research in Region 6 and synthesized our observations.) Some regions don’t have any schedules assigned and some schedules don’t have a particular region that keeps them. (I might be getting some details here wrong, but the key counter-intuitive realization is that “Regions are not just about geography”.)

* By “Worldwide rates”, we mean that the rates provided by CALC can be used for contracting labor anywhere in the world (even from, for example, overseas U.S. military facilities).

  * Certain regions, such as Region 6, have location-specific rates, so being able to support _non_-worldwide rates is something that may be needed in the near future.


* “Contract-awarded” prices are the rates that a vendor submits to GSA to become part of a schedule. These are the rates that CALC helps contract officers research so that new vendor contracts (or contracts that are up for renewal) are assured to have the “best rates.”

  * Contract-awarded prices are never actually what anyone pays for a labor service. Rather, they are essentially the highest price (“ceiling”) that could be paid to a vendor, but in practice there are always discounts that get applied/negotiated for a “task order” (sometimes called “service order”) is made.

  * A task order is when some group in the government actually hires a vendor’s personnel to do work.

* “Fully burdened” rates are inclusive of all surcharges and fees.

* The few research sessions we held with small businesses, sole proprietors, and the people who teach them how to pursue government contracts suggest a _ton_ of potential for CALC to help small businesses and sole proprietors understand the value of going through the hassle and cost of selling their services to the government. This potential was also seen during journey mapping for [Schedule 70 plain language](https://18f.gsa.gov/2016/06/21/using-plain-language-to-bridge-the-gap-between-government-and-industry/).

## Google Drive docs

* [CALC onboarding slides](https://docs.google.com/presentation/d/1NNnWP_uHzTGwoOaCrwNGb1ihGp076ZP0_u8trEjjJBk/edit#slide=id.g1afcaedca0_2_84)
* [Recommended goals, signals, and metrics](https://docs.google.com/spreadsheets/d/1EnlEaRs6iKsgGsJtZqvnq1lEYKhTMnQ-zAdHUOXKX9o/edit#gid=0)

### [Related 18F blog posts](https://18f.gsa.gov/tags/calc/)

* [Announcing the CALC tool: Making pricing research easier in federal procurement](https://18f.gsa.gov/2015/05/12/announcing-the-calc-tool/)
* [How the City of Boston is using GSA’s CALC tool](https://18f.gsa.gov/2015/11/10/boston-is-using-gsa-calc-tool/)
* [What happens when the whole team joins user interviews](https://18f.gsa.gov/2016/08/16/what-happens-when-the-whole-team-joins-user-interviews/)
* [Mark Trammell: Unlocking the true potential of public service](https://18f.gsa.gov/2016/08/26/mark-trammell-unlocking-the-true-potential-of-public-service/)

### Other
