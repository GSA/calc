import PropTypes from 'prop-types';
import React from 'react';
import { connect } from 'react-redux';

import { filterActive } from '../util';
import { setSinNumber as setSinNumberAction } from '../actions';

export function Sinnumber({ idPrefix, sinNumber, setSinNumber }) {
  const id = `${idPrefix}sinnumber`;
  const handleChange = (e) => { setSinNumber(e.target.value); };

  return (
    <div className="filter filter-site">
      <label htmlFor={id}>
Sin Number:
      </label>
      <input
        type="text"
        id={id}
        name="sinNumber"
        value={sinNumber}
        onChange={handleChange}
        className={filterActive(sinNumber !== '')}
      />
    
    </div>
  );
}

Sinnumber.propTypes = {
  sinNumber: PropTypes.string.isRequired,
  setSinNumber: PropTypes.func.isRequired,
  idPrefix: PropTypes.string,
};

Sinnumber.defaultProps = {
  idPrefix: '',
};

export default connect(
  state => ({ sinNumber: state.sinNumber }),
  { setSinNumber: setSinNumberAction },
)(Sinnumber);
