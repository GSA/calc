import React from 'react';

import createSortableColumn from './sortable-column';

const column = createSortableColumn({
  key: 'min_years_experience',
  title: 'Exper.',
  description: 'Minimum years of experience',
});

export const { HeaderCell } = column;

export const DataCell = column.connectDataCell(
  ({ className, value }) => {
    const years = (
      <span className="years">
        {value === 1 ? 'year' : 'years'}
      </span>
    );

    return (
      <td className={className}>
        {value} 
        {' '}
        {years}
      </td>
    );
  },
);
