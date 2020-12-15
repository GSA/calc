import PropTypes from 'prop-types';
import React from 'react';
import { connect } from 'react-redux';

import Tooltip from '../tooltip';
import { excludeRow as excludeRowAction } from '../../actions';
import RestoreExcluded from './restore-excluded';

export function HeaderCell() {
  return (
    <th scope="col" className="exclude">
      <RestoreExcluded />
    </th>
  );
}

function BaseDataCell({ excludeRow, result }) {
  const handleExcludeRow = rowId => (e) => {
    e.preventDefault();
    excludeRow(rowId);
  };

  const tooltip = 'Exclude this row from your search';

  return (
    <td className="cell column-exclude">
      <Tooltip text={tooltip}>
        <a /* eslint-disable-line jsx-a11y/anchor-is-valid */
          className="exclude-row"
          href=""
          onClick={handleExcludeRow(result.id)}
          aria-label={tooltip}
        >
          &times;
        </a>
      </Tooltip>
    </td>
  );
}

BaseDataCell.cellKey = 'exclude';

BaseDataCell.propTypes = {
  excludeRow: PropTypes.func.isRequired,
  result: PropTypes.object.isRequired,
};

export const DataCell = connect(
  null,
  { excludeRow: excludeRowAction },
)(BaseDataCell);
