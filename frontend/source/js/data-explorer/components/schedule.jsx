import PropTypes from 'prop-types';
import React from 'react';
import { connect } from 'react-redux';

import {
  setSchedule as setScheduleAction,
  setQueryBy as setQueryByAction
} from '../actions';
import { QUERY_BY_SCHEDULE } from '../constants';
import { scheduleLabels } from '../schedule-metadata';

export function Schedule({
  selectedSchedule, setSchedule, setQueryBy, queryBy
}) {
  const handleChange = (e) => {
    setSchedule(e.target.value);
    setQueryBy(QUERY_BY_SCHEDULE);
  };
  const defaultMsg = `In all ${Object.keys(scheduleLabels).length} contract vehicles`;
  // In most instances, we display legacy schedules as "Legacy Schedule," i.e., "Legacy MOBIS."
  // Here, however, we want to display the "Legacy" modifier in parenthesis after the name.
  // Since the legacy modifier only is found in schedule.full_name, we have to regex.
  const legacyPrefix = "Legacy ";
  const makeInput = (value, label) => {
    const id = value.replace(/ /g, '-').toLowerCase() || 'all-schedules';
    const makeLabel = (title) => {
      let scheduleLabel = title;
      let labelSuffix;
      if (title.includes(legacyPrefix)) {
        scheduleLabel = title.replace(legacyPrefix, '');
        labelSuffix = "(Legacy)";
      }
      return { scheduleLabel, labelSuffix };
    };
    const { scheduleLabel, labelSuffix } = makeLabel(label);
    return (
      <li key={id}>
        <input
          type="radio"
          id={id}
          name={id}
          value={value}
          onChange={handleChange}
          checked={selectedSchedule === value && queryBy === QUERY_BY_SCHEDULE}
        />
        <label htmlFor={id}>
          {scheduleLabel}
          <span className="label__suffix">
            {labelSuffix}
          </span>
        </label>
      </li>
    );
  };

  const makeChoices = labels => [
    { key: '', value: '', label: defaultMsg },
  ].concat(Object.keys(labels).map(
    value => ({ value, label: labels[value] }),
  )).map(({ value, label }) => (
    makeInput(value, label)
  ));

  return (
    <ul className="filter--schedule">
      {makeChoices(scheduleLabels, defaultMsg)}
    </ul>
  );
}

Schedule.propTypes = {
  selectedSchedule: PropTypes.string,
  setSchedule: PropTypes.func.isRequired,
  setQueryBy: PropTypes.func.isRequired,
  queryBy: PropTypes.string.isRequired,
};

Schedule.defaultProps = {
  selectedSchedule: '',
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
)(Schedule);
