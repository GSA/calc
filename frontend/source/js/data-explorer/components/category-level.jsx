/* global document */
import PropTypes from 'prop-types';

import React from 'react';

import { connect } from 'react-redux';

import SlideyPanel from './slidey-panel';
import CategoryLevelItem from './category-level-item';

import { parse as urlParse } from "url";

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
  addCatLevel, removeCatLevel, setSinNumber
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
const SOLUTIONS_ID_SUBCATEGORY_API = 'https://solutionsid.app.cloud.gov/api/v1/category_details/cat/';
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
      isMounted: true,
      expanded: false,
      categoryData: [],
      subCategoryData: [],
      catData: [],
      subCatData: [],
      sinData: '',
      checkedItems: new Map()
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

  componentWillUnmount() {
    document.removeEventListener('click', this.handleDocumentClick);
    document.removeEventListener('focus', this.handleDocumentClick, true);
    this.state.isMounted = false;
  }

  handleDocumentClick(e) {
    if (!this.state.expanded) {
      return;
    }

    // Whenever users click outside of our dropdown, hide it.
    if (!elementContains(this.dropdownEl, e.target)) {
      this.setState({ expanded: false });
    }

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

  handleCheckboxClick(inputId, level, isChecked) {
    // not sure if we really need to store a checked items list in state, but doing so for now
    this.setState((prevState) => ({
      checkedItems: prevState.checkedItems.set(inputId, isChecked),
    }));

    document.subCatData = this.state.subCategoryData;
    
    if (isChecked) {
      // Gets SIN NUBMER FOR THE SELECTED CATEGORY
      fetch(
        SOLUTIONS_ID_SUBCATEGORY_API + level.id + '?token=' + SOLUTIONSID_API_TOKEN
      )
        .then((response) => response.json())
        .then((subCategoryList) => {
          // append subCategoryList to subCategoryData state
          this.setState({ subCategoryData: this.state.subCategoryData.concat(subCategoryList.all_categories) }, () => {
            // call add category level action
            this.props.addCatLevel(level);
            // add sin numbers to filter state
            this.handleSinNumbers();
          })       
        });
    // removes selected category from state
    } else {
      // call remove category level action
      this.props.removeCatLevel(level);
      // remove the selected category data from subCategoryData state, note the trailing space at end, TODO will be fixed in data response
      let filteredSubCategories = this.state.subCategoryData.filter(element => element.category_code !== `${level.code} `);
      this.setState({subCategoryData: filteredSubCategories}, () => {
        this.handleSinNumbers();
      });     
    }
  }

  findIndex(array, attr, value) {
      for(var i = 0; i < array.length; i +=1) {
          if(array[i][attr] === value) {
              return i;
          }
      }
      return -1;
  }

  handleSinNumbers(status) {
    let urlSin = '';
    let catSinNumbers = '';

    if (this.state.subCategoryData.length > 0 && this.state.subCategoryData !== null) {
      let sin = this.state.subCategoryData.map((item) => item.legacy_sin.replace(/ /g, '-') + ';').join('');
      // replace all current selected catSinNumbers in dispatch to state, setSinNumber action propType
      this.props.setSinNumber(sin.slice(0, -1));
    } else {
      this.props.setSinNumber('');
    }  
  }

  render() {
    const { levels, idPrefix, history } = this.props;

    let inputs = '';

    let cats = this.state.categoryData;

    if(cats[0] !== undefined) {
        let scheduleCategories = JSON.stringify(cats[0].scheduleCategories);
        let selectedCategories = JSON.stringify(levels);

        let catsArray = JSON.parse(scheduleCategories);

        inputs = Object.keys(catsArray).map((value => {
            const id = idPrefix + value;
            return (
                <CategoryLevelItem
                    key={JSON.stringify(value)}
                    id={id}
                    checked={this.state.checkedItems.get(id)}
                    value={catsArray[value]}
                    onCheckboxClick={this.handleCheckboxClick}
                />
            );
        }));

    }

    let linkContent1;

    if (levels.length === 0) {

      linkContent1 = (
        <span className="eduSelect">
(all)
          <span className="usa-sr-only">
            {' '}
to reveal Schedule Categories options
          </span>
        </span>
      );
    } else {

      const selectedLevels = levels.map((value) => {
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

    return (
      <div>
        <label htmlFor={catLevelId}>
Category:
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
Category:
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
  addCatLevel: PropTypes.func.isRequired,
  removeCatLevel: PropTypes.func.isRequired,
  setSinNumber: PropTypes.func.isRequired,
  history: PropTypes.string,
};

CategoryLevel.defaultProps = {
  idPrefix: 'category-level-',
};

export default connect(
  state => ({ levels: state.category }),
  { addCatLevel, removeCatLevel, setSinNumber }
)(CategoryLevel);

