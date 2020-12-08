import PropTypes from 'prop-types';
import React from 'react';
import { connect } from 'react-redux';

import Schedule from './schedule';
import Vendor from './vendor-search';
import ContractNum from './contract-search';
import {
  QUERY_BY_SCHEDULE,
  QUERY_BY_VENDOR,
  QUERY_BY_CONTRACT
} from '../constants';
import { scheduleLabels } from '../schedule-metadata';

import {
  autobind,
  handleEnterOrSpace,
} from '../util';


export class SearchCategory extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      expanded: false,
    };
    autobind(this, ['toggleDropdown', 'closeMenuOnClick', 'createButtonText']);
  }

  toggleDropdown() {
    this.setState({
      expanded: !this.state.expanded, /* eslint-disable-line react/no-access-state-in-setstate */
    });
  }

  closeMenuOnClick() {
    this.setState({
      expanded: false,
    });
  }

  createButtonText() {
    const { selectedSchedule, queryBy } = this.props;
    let searchSummary;
    if (queryBy === QUERY_BY_SCHEDULE) {
      const allSchedsLabel = `${Object.keys(scheduleLabels).length} contract vehicles`;

      searchSummary = (
        <div>
          <strong>
            Search labor categories
          </strong>
          <span>
            in
            {' '}
            { scheduleLabels[selectedSchedule] || allSchedsLabel }
          </span>
        </div>
      );
    } else if (queryBy === QUERY_BY_VENDOR) {
      searchSummary = (
        <strong>
          Search for a vendor
        </strong>
      );
    } else if (queryBy === QUERY_BY_CONTRACT) {
      searchSummary = (
        <strong>
          Search for a contract
        </strong>
      );
    }
    return searchSummary;
  }

  render() {
    return (
      <div className="html-dropdown">
        <button
          type="button"
          className="html-dropdown__trigger"
          aria-controls="data-explorer__search-category" /* eslint-disable-line jsx-a11y/aria-proptypes */
          onClick={this.toggleDropdown}
          onKeyDown={handleEnterOrSpace(this.toggleDropdown)}
          aria-expanded={this.state.expanded}
        >
          { this.createButtonText() }
        </button>
        {/* setting a key event on this div makes it impossible to select
          * an option with the keyboard. It's just a nicety, so should be OK. */}
        <div /* eslint-disable-line max-len, jsx-a11y/click-events-have-key-events, jsx-a11y/interactive-supports-focus */
          className="html-dropdown__choices"
          id="data-explorer__search-category"
          onClick={this.closeMenuOnClick}
          aria-hidden={!this.state.expanded}
          role="menu"
        >
          <h3>
            Search vendors and contracts
          </h3>
          <Vendor />
          <ContractNum />
          <h3>
            Search labor categories
          </h3>
          <Schedule />
        </div>
      </div>
    );
  }
}

SearchCategory.propTypes = {
  selectedSchedule: PropTypes.string,
  queryBy: PropTypes.string.isRequired,
};

SearchCategory.defaultProps = {
  selectedSchedule: '',
};

export default connect(
  state => ({
    selectedSchedule: state.schedule,
    queryBy: state.query_by,
  })
)(SearchCategory);
