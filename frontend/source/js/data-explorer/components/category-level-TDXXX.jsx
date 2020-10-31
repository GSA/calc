/* global document */

import PropTypes from 'prop-types';

import React from 'react';
import { connect } from 'react-redux';

import SlideyPanel from './slidey-panel';
import CategoryLevelItem from './category-level-item';

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
    };
    autobind(this, ['handleToggleMenu', 'handleDocumentClick',
      'handleCheckboxClick']);
  }

  componentDidMount() {
    document.addEventListener('click', this.handleDocumentClick);
    document.addEventListener('focus', this.handleDocumentClick, true);
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
    console.log("THISSSPROPPPS"+JSON.stringify(this.props));
    const inputs = Object.keys(EDU_LABELS).map((value) => {
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
    });
    let linkContent;

    if (levels.length === 0) {
      console.log("1111111111111");
      linkContent = (
        <span className="eduSelect">
Select
          <span className="usa-sr-only">
            {' '}
to reveal Category TD3 options
          </span>
        </span>
      );
    } else {
      console.log("222222222222");
      const selectedLevels = levels.map((value) => {
        const label = CAT_LABELS[value];
        return (
          <span key={value} title={label}>
            {label}
          </span>
        );
      });
      linkContent = (
        <div className="multiSel">
          {selectedLevels}
        </div>
      );
    }

    const eduLevelId = `${this.props.idPrefix}category_level`;

    return (
      <div>
        <label htmlFor={catLevelId}>
CAT TD level:
        </label>
        <dl
          id={catLevelId}
          className="dropdown"
          ref={(el) => { this.dropdownEl = el; }}
        >
          <dt>
            <a /* eslint-disable-line jsx-a11y/anchor-is-valid */
              href=""
              onClick={this.handleToggleMenu}
              role="button"
              aria-expanded={this.state.expanded.toString()}
              onKeyDown={handleEnterOrSpace(this.handleToggleMenu)}
              className={filterActive(levels.length !== 0)}
            >
              {linkContent}
            </a>
          </dt>

          <dd>
            <div className="multiSelect">
              <fieldset>
                <legend className="usa-sr-only">
CAT TD2 level:
                </legend>

                <SlideyPanel
                  component="ul"
                  expanded={!this.state.expanded}
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
};

CategoryLevel.defaultProps = {
  idPrefix: 'category-level-',
};

export default connect(
  state => ({ levels: state.category }),
  { toggleCatLevel },
)(CategoryLevel);
