import PropTypes from 'prop-types';
import React from 'react';
import { connect } from 'react-redux';

import { setQueryType as setQueryTypeAction } from '../actions';
import {
  QUERY_TYPE_MATCH_EXACT,
  QUERY_TYPE_LABELS,
} from '../constants';

const INPUT_INFOS = {
  [QUERY_TYPE_MATCH_EXACT]: {
    idSuffix: 'match_exact',
  },
};

export function QueryType({ queryType, setQueryType, idPrefix }) {
  const input = (type) => {
    const { idSuffix } = INPUT_INFOS[type];
    const id = `${idPrefix}${idSuffix}`;

    return (
      <li>
        <input
          id={id}
          type="checkbox"
          name="query_type"
          value={queryType}
          checked={queryType === QUERY_TYPE_MATCH_EXACT}
          onChange={() => { setQueryType(queryType); }}
        />
        <label htmlFor={id}>
          {QUERY_TYPE_LABELS[type]}
        </label>
      </li>
    );
  };

  return (
    <ul role="group" aria-label="Labor category query type">
      {input(QUERY_TYPE_MATCH_EXACT)}
    </ul>
  );
}

QueryType.propTypes = {
  queryType: PropTypes.string.isRequired,
  setQueryType: PropTypes.func.isRequired,
  idPrefix: PropTypes.string,
};

QueryType.defaultProps = {
  idPrefix: 'query_type_',
};

export default connect(
  state => ({ queryType: state.query_type }),
  { setQueryType: setQueryTypeAction },
)(QueryType);
