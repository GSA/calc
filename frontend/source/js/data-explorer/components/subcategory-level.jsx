/* eslint-disable */
/* global document */
import PropTypes from 'prop-types';
import React from 'react';
import { connect } from 'react-redux';
import SlideyPanel from './slidey-panel';
import SubCategoryLevelItem from './subcategory-level-item';

import {
  autobind,
  handleEnterOrSpace,
  filterActive,
} from '../util';

import {
  addSubCatLevel, removeSubCatLevel, setSinNumber
} from '../actions';

const SOLUTIONS_ID_SUBCATS_API = 'https://solutionsid.app.cloud.gov/api/v1/schedule-subcategories';
const SOLUTIONS_ID_SUBCATEGORY_API = 'https://solutionsid.app.cloud.gov/api/v1/category_details/cat/';

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

/**
 * The following logic was created to mimic the following
 * legacy jQuery behavior:
 *
 *   Dropdown with Multiple checkbox select with jQuery - May 27, 2013
 *   (c) 2013 @ElmahdiMahmoud
 *   license: http://www.opensource.org/licenses/mit-license.php
 */
export class SubCategoryLevel extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      isMounted: true,
      expanded: false,
      categoryData: [],
      subCategoryData: [],
      checkedItems: new Map()
    };
    autobind(this, ['handleToggleMenu', 'handleDocumentClick', 'handleCheckboxClick']);
  }

  componentDidMount() {
    document.addEventListener('click', this.handleDocumentClick);
    document.addEventListener('focus', this.handleDocumentClick, true);

    fetch(SOLUTIONS_ID_SUBCATS_API)
      .then((response) => response.json())
      .then(subCategoryList => {
        this.setState({ subCategoryData: subCategoryList });
      });

    document.catData = this.state.subCategoryData;
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
      expanded: !this.state.expanded, /* eslint-disable-line
               react/no-access-state-in-setstate */
    });
  }

  handleCheckboxClick(inputId, level, isChecked) {
    //console.log("CLICKEDDDDD:" + JSON.stringify(inputId) + " - " + JSON.stringify(isChecked) + " === " +JSON.stringify(level));
    //CLICKEDDDDD:"subcategory-level-15" - true === {"category_id":1,"code":"A02","created_at":null,"description":null,"id":4,"legacy_sin":"58 10","rpt_off":"P","sin":"541990AV","sin_title":"541990AV Professional Audio/Video Services","title":"Audio Visual Services","updated_at":null}
    //category-level.jsx?09fe:100 CLICKEDDDDD:"category-level-1" - true === {"code":"B","id":2,"title":"Facilities"}
    // not sure if we really need to store a checked items list in state,
    // but doing so for now
    this.setState((prevState) => ({
      checkedItems: prevState.checkedItems.set(inputId, isChecked),
    }));
    console.log("STATE:" + JSON.stringify(this.state));
    document.subCatData = this.state.subCategoryData;
    
    if (isChecked) {
      this.props.addSubCatLevel(level.legacy_sin);
      //this.handleSinNumbers();
      this.props.setSinNumber(level.legacy_sin.replace(/ /g, "-")); //.slice(0, -1)
    // removes selected category from state
    } else {
      // call remove category level action
      this.props.removeSubCatLevel(level.legacy_sin);
      /*
      // remove the selected category data from subCategoryData state,
      // note the trailing space at end, TODO will be fixed in data response
      let filteredSubCategories = this.state.subCategoryData.filter(
        element => element.category_code !== `${level.code} `);
      this.setState({ subCategoryData: filteredSubCategories }, () => {
        this.handleSinNumbers();
      }); */
    }
  }

  /*findIndex(array, attr, value) {
    for (var i = 0; i < array.length; i +=1) {
      if (array[i][attr] === value) {
          return i;
      }
    }
    return -1;
  }
  541922 Commercial Photography Services
  ?sinNumber=541%204E
  ?sinNumber=541%204E
        "legacy_sin": "541 4E",
        "rpt_off": "T",
        "sin": "541922",
        "sin_title": "541922 Commercial Photography Services",
  */

  handleSinNumbers() {
    if (this.state.subCategoryData.length > 0 && this.state.subCategoryData !== null) {
      ///const sin = this.state.subCategoryData.map((item) => item.legacy_sin.replace(/ /g, "-") + ";").join('');
      // replace all current selected catSinNumbers in dispatch to state,
      // setSinNumber action propType
      //this.props.setSinNumber(legacy_sin.replace(/ /g, "-")); //.slice(0, -1)
    } else {
      this.props.setSinNumber('');
    }
  }

  render() {
    const { levels, idPrefix } = this.props;

    let inputs = '';

    const cats = this.state.subCategoryData;
    if (cats[0] !== undefined) {
      let scheduleCategories = JSON.stringify(cats[0].scheduleCategories);
      let selectedCategories = JSON.stringify(levels);

      const catsArray = JSON.parse(scheduleCategories);

      inputs = Object.keys(catsArray).map((value => {
        const id = idPrefix + value;
        return (
          <SubCategoryLevelItem
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
    //console.log("LEVELS LENGTH SHOULD BE >0"); console.log(JSON.stringify(levels));
    if (levels.length === 0) {
      linkContent1 = (
          <span className="eduSelect">
(all)
          <span className="usa-sr-only">
              {' '}
to reveal Schedule Subcategories options
          </span>
        </span>
      );
    } else {
      const selectedLevels = levels.map((value) => {
        const label = value.title; // The label in the input field
        // populated when user selects one or more categories
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

    const catLevelId = `${this.props.idPrefix}subcategory_level`;

    return (
      <div>
          <label htmlFor={catLevelId}>
Subcategory:
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
Subcategory:
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

SubCategoryLevel.propTypes = {
  levels: PropTypes.array.isRequired,
  idPrefix: PropTypes.string,
  addSubCatLevel: PropTypes.func.isRequired,
  removeSubCatLevel: PropTypes.func.isRequired,
  setSinNumber: PropTypes.func.isRequired,
};

SubCategoryLevel.defaultProps = {
  idPrefix: 'subcategory-level-',
};

export default connect(
  state => ({ levels: state.category }),
  { addSubCatLevel, removeSubCatLevel, setSinNumber }
)(SubCategoryLevel);