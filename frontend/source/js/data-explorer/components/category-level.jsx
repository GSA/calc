/* global document */

import PropTypes from 'prop-types';

import React from 'react';
import { connect } from 'react-redux';
/* import { browserHistory } from 'react-router';
import * as querystring from 'querystring';  */

import SlideyPanel from './slidey-panel';
import CategoryLevelItem from './category-level-item';
//import EducationLevelItem from './category-level-item';

import { parse as urlParse } from "url";

import { setSinNumber as setSinNumberAction } from '../actions';

import {
  autobind,
  handleEnterOrSpace,
  filterActive,
  parseQueryString,
} from '../util';

import {
  CAT_LABELS,
} from '../constants';

import {
  toggleCatLevel,
} from '../actions';

// TODO: We could just use jQuery for this, but I wanted to decouple
// the new React code from jQuery as much as possible for now.
function elementContains(container, contained) {
  let target = contained.parentNode;

  while (target) {
    if (target === container) {
      return true;
    }
    target = target.parentNode;
  }
  return false;
}

const SOLUTIONS_ID_API = 'https://solutionsid.app.cloud.gov/api/v1/schedule_cats?token=';
// const SOLUTIONS_ID_API = 'https://solutionsid.app.cloud.gov/api/v1/schedule_category?token=';
const SOLUTIONS_ID_SUBCATEGORY_API = 'https://solutionsid.app.cloud.gov/api/v1/schedule_subcategory/cat/';
const SOLUTIONSID_API_TOKEN = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpZCI6NSwiZXhwIjoxNjA2MzEzNTQ0fQ.L9OCuCruD8tDdggj-JcC65dkvLkKVBhqUFLeXiwW9Jo';

/**
 * The following logic was created to mimic the following
 * legacy jQuery behavior:
 *
 *   Dropdown with Multiple checkbox select with jQuery - May 27, 2013
 *   (c) 2013 @ElmahdiMahmoud
 *   license: http://www.opensource.org/licenses/mit-license.php
 */

export class CategoryLevel extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      expanded: false,
      categoryData: [],
      subCategoryData: [],
      catData: [],
      subCatData: [],
    };
    autobind(this, ['handleToggleMenu', 'handleDocumentClick',
      'handleCheckboxClick']);
  }

  componentDidMount() {
    document.addEventListener('click', this.handleDocumentClick);
    document.addEventListener('focus', this.handleDocumentClick, true);
    fetch(SOLUTIONS_ID_API + SOLUTIONSID_API_TOKEN)
      .then( (response) => response.json())
      .then(categoryList => {
        this.setState({ categoryData: categoryList });
      });
    document.catData = this.state.categoryData;
  }

  componentWillMount() {
    console.log(JSON.stringify(this.props));
    console.log('%%%%%%%%%%%%%%%%%%%');
    console.log(JSON.stringify(this.state));
    // console.log('%%%%%%%%%' + this.window.location + '%%%%%%%%%%');
      console.log(typeof window);
    /* if (typeof window !== 'undefined') {
           // window.location.href = "/?sinNumber=202";
    }


    const qsFields = parseQueryString(
      this.window.location.search.substring(1)
    ); // substring after '?' char
    console.log(qsFields);
    const qsFields = parseQueryString(
      this.window.location.search.substring(1)
    ); // substring after '?' char
    console.log("*******" +  qsFields);*/
            console.log('this is: ', this);

      console.log("SUB RESPONSE: " + this.state.subCategoryData);
      //let url = this.window.location.href;
      //console.log(url.pathname + " URL SEARCH: " + url.search);
      // console.log(urlParse(server.requests[0].url));
  }

  componentWillUnmount() {
    document.removeEventListener('click', this.handleDocumentClick);
    document.removeEventListener('focus', this.handleDocumentClick, true);
  }

  handleDocumentClick(e) {
    if (!this.state.expanded) {
      return;
    }

    // Whenever users click outside of our dropdown, hide it.
    if (!elementContains(this.dropdownEl, e.target)) {
      this.setState({ expanded: false });
    }
    console.log("INSIDE handleDocumentClick");
    /*
    const qsFields = parseQueryString(
      this.window.location.search.substring(1)
    ); // substring after '?' char
    console.log(qsFields);
    */
  }

  handleToggleMenu(e) {
    // TODO: The original jQuery logic used .slideDown() here, it'd
    // be nice if we could use some sort of transition too.
    // TD: togggles expanded to true or false

    e.preventDefault();
    this.setState({
      expanded: !this.state.expanded, /* eslint-disable-line react/no-access-state-in-setstate */
    });
  }

  handleCheckboxClick(level) {
      console.log("CLICKEDDDDD:" + JSON.stringify(level.id));
      console.log(level.title);
      // Gets SIN NUBMER FOR THE SELECTED CATEGORY
      fetch(SOLUTIONS_ID_SUBCATEGORY_API + level.id + '?token=' + SOLUTIONSID_API_TOKEN)
      .then( (response) => response.json() )
      .then(subCategoryList => {
        this.setState({ subCategoryData: subCategoryList });
      });
      document.subCatData = this.state.subCategoryData;
      this.props.toggleCatLevel(level);

      //SIN NUMBERS  874 503; 874 507
      /*if (typeof window !== 'undefined') {
          window.location.href = "/?sinNumber=874 503; 874 507; 222; 223";
      }*/

  }

  findIndex(array, attr, value) {
      for(var i = 0; i < array.length; i +=1) {
          if(array[i][attr] === value) {
              return i;
          }
      }
      return -1;
  }

  render() {
    const { levels, idPrefix, history } = this.props;
    //console.log("-----------------------");
    //console.log(JSON.stringify(this.props));
    let inputs = '';

    let cats = this.state.categoryData;

    if(cats[0] !== undefined) {
        let scheduleCategories = JSON.stringify(cats[0].scheduleCategories);
        let selectedCategories = JSON.stringify(levels);

        let catsArray = JSON.parse(scheduleCategories);

        inputs = Object.keys(catsArray).map((value => {

            let chex = false;
            const id = idPrefix + value;
            if (levels.length > 0) {
                // @TODO FIX, works for the last value only
                const selectedLevels = levels.map((val) => {
                    chex = (val.id-1 == value);
                });
            }
            //console.log("BUILDING:::");
            //console.log("key: " + JSON.stringify(value ) + " catsArray[key]: " + catsArray[value]);
            //console.log("key: " + JSON.stringify(value ) +  " ID: " + id + " CHECKED: " + chex + " Value: " + catsArray[value-1].id);
            //console.log("------------------------------------------------------------------------------------");
            return (
                <CategoryLevelItem
                    key={JSON.stringify(value)}
                    id={id}
                    checked={chex}
                    value={catsArray[value]}
                    onCheckboxClick={this.handleCheckboxClick}
                />
            );
        }));
                  // OLD VALUE: value={catsArray[value]}

    }

    let linkContent1;

    if (levels.length === 0) {

      linkContent1 = (
        <span className="eduSelect">
Select
          <span className="usa-sr-only">
            {' '}
to reveal Schedule Categories options
          </span>
        </span>
      );
    } else {
      console.log("SELECTED LEVELS2:"+JSON.stringify(levels));
      //let searchParams = this.props.location.pathname;

      const selectedLevels = levels.map((value) => {
      /* URL history.push({
          pathname: '/',
          search: '?sin=222'
        });
        var path = windowLocation.pathname + windowLocation.search;
        console.log("PATH: " + path);
        let currentUrlParams = new URLSearchParams(window.location.search);
        currentUrlParams.set('sin', 222);
        console.log(window.location.pathname + "?" + currentUrlParams.toString() + "CURRENT URL PARAMS: "+currentUrlParams);
*/
        // this.props.history.push(window.location.pathname + "?" + currentUrlParams.toString());

        const label = value.title; //The label in the input field populated when user selects one or more categories
        return (
          <span key={value.code} title={label}>
            {label}
          </span>
        );
      });
      linkContent1 = (
        <div className="multiSel">
          {selectedLevels}
        </div>
      );
    }

    const catLevelId = `${this.props.idPrefix}category_level`;

    console.log("CATTTTT catLevelId: " + catLevelId);
    console.log('this state is: ', this.state);

    console.log("SUB RESPONSE: " + JSON.stringify(this.state.subCategoryData));
      //let url = this.window.location.href;
      //console.log(url.pathname + " URL SEARCH: " + url.search);
      // console.log(urlParse(server.requests[0].url));
    return (
      <div>
        <label htmlFor={catLevelId}>
Category1:
        </label>
        <dl
          id={catLevelId}
          className="dropdown"
          ref={(el) => { this.dropdownEl = el; }}
        >
          <dt>
            <a
              href=""
              onClick={this.handleToggleMenu}
              role="button"
              aria-expanded={this.state.expanded.toString()}
              onKeyDown={handleEnterOrSpace(this.handleToggleMenu)}
              className={filterActive(levels.length !== 0)}
            >
              {linkContent1}
            </a>
          </dt>
          <dd>
            <div className="multiSelect">
              <fieldset>
                <legend className="usa-sr-only">
Category level:
                </legend>

                <SlideyPanel
                  component="ul"
                  expanded={this.state.expanded}
                >
                  {inputs}
                </SlideyPanel>
              </fieldset>
            </div>
          </dd>

        </dl>
      </div>
    );
  }
}

CategoryLevel.propTypes = {
  levels: PropTypes.array.isRequired,
  idPrefix: PropTypes.string,
  toggleCatLevel: PropTypes.func.isRequired,
  history: PropTypes.string,
};

CategoryLevel.defaultProps = {
  idPrefix: 'category-level-',
};

export default connect(
  state => ({ levels: state.category }),
  { toggleCatLevel },
)(CategoryLevel);
