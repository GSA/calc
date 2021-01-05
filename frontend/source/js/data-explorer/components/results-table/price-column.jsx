import React from 'react';
import { connect } from 'react-redux';

import createSortableColumn from './sortable-column';
import { formatPriceWithCents } from '../../util';

const column = createSortableColumn({
  key: 'current_price',
  title: 'Price',
  description: 'Ceiling price',
});

export function priceForContractYear(contractYear, result) {
  let key = 'current_price';

  if (contractYear === '1') {
    key = 'next_year_price';
  } else if (contractYear === '2') {
    key = 'second_year_price';
  }

  return result[key];
}

export const { HeaderCell } = column;

export const DataCell = column.connectDataCell(connect(
  state => ({ contractYear: state['contract-year'] }),
)(
  ({ className, result, contractYear }) => {
    const price = priceForContractYear(contractYear, result);

    return (
      <td className={className}>
        $
        {formatPriceWithCents(price)}
      </td>
    );
  },
));
