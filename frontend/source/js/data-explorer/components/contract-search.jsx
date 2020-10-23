import PropTypes from 'prop-types';
import React from 'react';
import { connect } from 'react-redux';

import {
  setSchedule as setScheduleAction,
  setQueryBy as setQueryByAction
} from '../actions';
import { QUERY_BY_CONTRACT } from '../constants';

export function ContractNum({ setSchedule, setQueryBy, queryBy }) {
  const handleClick = (e) => {
    // unset selectedSchedule if it has been previously set
    setSchedule('');
    setQueryBy(e.target.value);
  };

  return (
    <button
      type="button"
      id={QUERY_BY_CONTRACT}
      name={QUERY_BY_CONTRACT}
      className={queryBy === QUERY_BY_CONTRACT ? 'query-by__selected' : ''}
      value={QUERY_BY_CONTRACT}
      onClick={handleClick}
    >
      <span />
      Find a contract by number
    </button>
  );
}

ContractNum.propTypes = {
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
)(ContractNum);
