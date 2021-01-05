import PropTypes from 'prop-types';
import React from 'react';
import { connect } from 'react-redux';

import { filterActive } from '../util';
import { makeOptions } from './util';
import { setSecurityClearance as setSecurityClearanceAction } from '../actions';
import { SECURITY_CLEARANCE_LABELS } from '../constants';

export function SecurityClearance({ idPrefix, securityClearance, setSecurityClearance }) {
  const id = `${idPrefix}security_clearance`;
  const handleChange = (e) => { setSecurityClearance(e.target.value); };

  return (
    <div className="filter filter-security-clearance">
      <label htmlFor={id}>
        Security Clearance:
      </label>
      <select
        id={id}
        name="security_clearance"
        value={securityClearance}
        onChange={handleChange}
        className={filterActive(securityClearance !== '')}
      >
        {makeOptions(SECURITY_CLEARANCE_LABELS)}
      </select>
    </div>
  );
}

SecurityClearance.propTypes = {
  securityClearance: PropTypes.string.isRequired,
  setSecurityClearance: PropTypes.func.isRequired,
  idPrefix: PropTypes.string,
};

SecurityClearance.defaultProps = {
  idPrefix: '',
};

export default connect(
  state => ({ securityClearance: state.securityClearance }),
  { setSecurityClearance: setSecurityClearanceAction },
)(SecurityClearance);
