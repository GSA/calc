import React from 'react';

import createSortableColumn from './sortable-column';

const column = createSortableColumn({
  key: 'certifications',
  title: 'Certifications',
  description: 'certifications',
});


export const { HeaderCell } = column;

export const DataCell = column.connectDataCell(
  ({ className, value }) => (
    <td className={className}>
      {value || 'N/A'}
    </td>
  ),
);
