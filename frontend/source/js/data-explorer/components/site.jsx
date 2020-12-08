import PropTypes from 'prop-types';
import React from 'react';
import { connect } from 'react-redux';

import { filterActive } from '../util';
import { makeOptions } from './util';
import { setSite as setSiteAction } from '../actions';
import { SITE_LABELS } from '../constants';

export function Site({ idPrefix, site, setSite }) {
  const id = `${idPrefix}site`;
  const handleChange = (e) => { setSite(e.target.value); };

  return (
    <div className="filter filter-site">
      <label htmlFor={id}>
        Worksite:
      </label>
      <select
        id={id}
        name="site"
        value={site}
        onChange={handleChange}
        className={filterActive(site !== '')}
      >
        {makeOptions(SITE_LABELS)}
      </select>
    </div>
  );
}

Site.propTypes = {
  site: PropTypes.string.isRequired,
  setSite: PropTypes.func.isRequired,
  idPrefix: PropTypes.string,
};

Site.defaultProps = {
  idPrefix: '',
};

export default connect(
  state => ({ site: state.site }),
  { setSite: setSiteAction },
)(Site);
