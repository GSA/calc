import PropTypes from 'prop-types';
import React from 'react';
import { connect } from 'react-redux';

import { filterActive } from '../util';
import { makeOptions } from './util';
import { setBusinessSize as setBusinessSizeAction } from '../actions';
import { BUSINESS_SIZE_LABELS } from '../constants';

export function BusinessSize({ idPrefix, size, setSize }) {
  const id = `${idPrefix}business_size`;
  const handleChange = (e) => { setSize(e.target.value); };

  return (
    <div className="filter filter-business_size">
      <label htmlFor={id}>
Business size:
      </label>
      <select
        id={id}
        name="business_size"
        value={size}
        onChange={handleChange}
        className={filterActive(size !== '')}
      >
        {makeOptions(BUSINESS_SIZE_LABELS)}
      </select>
    </div>
  );
}

BusinessSize.propTypes = {
  size: PropTypes.string.isRequired,
  setSize: PropTypes.func.isRequired,
  idPrefix: PropTypes.string,
};

BusinessSize.defaultProps = {
  idPrefix: '',
};

export default connect(
  state => ({ size: state.business_size }),
  { setSize: setBusinessSizeAction },
)(BusinessSize);
