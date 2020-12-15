import PropTypes from 'prop-types';
import React from 'react';
import { connect } from 'react-redux';

import {
  setSchedule as setScheduleAction,
  setQueryBy as setQueryByAction
} from '../actions';
import { QUERY_BY_VENDOR } from '../constants';

export function Vendor({ setSchedule, setQueryBy, queryBy }) {
  const handleClick = (e) => {
    // unset selectedSchedule if it has been previously set
    setSchedule('');
    setQueryBy(e.target.value);
  };

  return (
    <button
      type="button"
      id={QUERY_BY_VENDOR}
      name={QUERY_BY_VENDOR}
      className={queryBy === QUERY_BY_VENDOR ? 'query-by__selected' : ''}
      value={QUERY_BY_VENDOR}
      onClick={handleClick}
    >
      <span />
      Find a vendor by name
    </button>
  );
}

Vendor.propTypes = {
  setQueryBy: PropTypes.func.isRequired,
  setSchedule: PropTypes.func.isRequired,
  queryBy: PropTypes.string.isRequired,
};

export default connect(
  state => ({
    selectedSchedule: state.schedule,
    queryBy: state.query_by,
  }),
  {
    setSchedule: setScheduleAction,
    setQueryBy: setQueryByAction,
  },
)(Vendor);
