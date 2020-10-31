/* global document */

import PropTypes from 'prop-types';

import React from 'react';
import { connect } from 'react-redux';

import SlideyPanel from './slidey-panel';
import CategoryLevelItem from './category-level-item';
//import EducationLevelItem from './category-level-item';

import {
  autobind,
  handleEnterOrSpace,
  filterActive,
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
      catData: [],
    };
    autobind(this, ['handleToggleMenu', 'handleDocumentClick',
      'handleCheckboxClick']);
  }

  componentDidMount() {
    document.addEventListener('click', this.handleDocumentClick);
    document.addEventListener('focus', this.handleDocumentClick, true);
    fetch(SOLUTIONS_ID_API + SOLUTIONSID_API_TOKEN)
    //fetch(TEST_API)
      .then( (response) => response.json())
      .then(categoryList => {
        this.setState({ categoryData: categoryList });
      });
    document.catData = this.state.categoryData;
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
    this.props.toggleCatLevel(level);
  }

  render() {
    const { levels, idPrefix } = this.props;
    let inputs = '';

    let cats = this.state.categoryData;

    if(cats[0] !== undefined) {
        let scheduleCategories = JSON.stringify(cats[0].scheduleCategories);
        //console.log(cats[0].count);
        let catsArray = JSON.parse(scheduleCategories);
        inputs = Object.keys(catsArray).map((value => {
            const id = idPrefix + value;
            console.log("CAT IDDDD LEVELS INDEXXXX:   " + levels.indexOf(value));
            console.log("NEGDJE ID"+idPrefix + value + " "  + catsArray[value].title);

            return (
                <CategoryLevelItem
                    key={value}
                    id={id}
                    checked={levels.indexOf(value) >= 0}
                    value={catsArray[value]}
                    onCheckboxClick={this.handleCheckboxClick}
                />
            );
        }));

    }
    console.log("TUUUSAMMMM"+JSON.stringify(this.state.categoryData[0]));

    console.log("==============");
    //console.log(Object.keys(cats)[0]);
    console.log("SAMMMM"+JSON.stringify(this.state.catData));
    console.log("------------");

           /*     const inputs = Object.keys(CAT_LABELS).map((value) => {
            const id = idPrefix + value;

            return (
                <CategoryLevelItem
                    key={value}
                    id={id}
                    checked={levels.indexOf(value) >= 0}
                    value={value}
                    onCheckboxClick={this.handleCheckboxClick}
                />
            );
        });*/
    // }

    /*const inputs = Object.keys(JSON.parse(this.state.categoryData)).map((value) => {
      const id = idPrefix + value;
      console.log("VALUE: " + value);

      <ul>
        {
          this.state.categoryData.map(
            (cat) => (
              <li key={cat.id}>{cat.title}</li>
            )
          )
        }
      </ul>


      return (
        <CategoryLevelItem
          key={value}
          id={id}
          checked={levels.indexOf(value) >= 0}
          value={value}
          onCheckboxClick={this.handleCheckboxClick}
        />
      );
    });*/

    let linkContent1;

    if (levels.length === 0) {
      //console.log("ORIGINAL LEVELS:" + JSON.Stringify(levels));
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
      console.log("SELECTED LEVELS:"+JSON.stringify(levels));
      const selectedLevels = levels.map((value) => {
        console.log("111111");
        const label = CAT_LABELS[value];
        return (
          <span key={value} title={label}>
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
    console.log("CATTTTT catLevelId: "+catLevelId);
    /*
    <ul>
      {
        this.state.categoryData.map(
          (cat) => (
            <li key={cat.id}>{cat.title}</li>
          )
        )
      }
    </ul>
    */
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
  idPrefix: PropTypes.array,
  toggleCatLevel: PropTypes.func.isRequired,
};

CategoryLevel.defaultProps = {
  idPrefix: 'category-level-',
};

export default connect(
  state => ({ levels: state.category }),
  { toggleCatLevel },
)(CategoryLevel);
