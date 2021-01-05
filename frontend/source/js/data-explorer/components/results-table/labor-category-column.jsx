import React from 'react';

import createSortableColumn from './sortable-column';

const column = createSortableColumn({
  key: 'labor_category',
  title: 'Labor category',
});

export const { HeaderCell } = column;

export const DataCell = column.connectDataCell(
  ({ className, value }) => (
    <th className={className} scope="row">
      {value}
    </th>
  ),
);
