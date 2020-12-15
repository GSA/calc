import {
  GenericHeaderCell,
  createHeaderCellConnector,
} from './sortable-header-cell';

import {
  GenericDataCell,
  createDataCellConnector,
} from './sortable-data-cell';

export default function createSortableColumn({
  description,
  title,
  key,
}) {
  const connectHeaderCell = createHeaderCellConnector(description, title, key);
  const connectDataCell = createDataCellConnector(key);
  const HeaderCell = connectHeaderCell(GenericHeaderCell);
  const DataCell = connectDataCell(GenericDataCell);

  return { HeaderCell, DataCell, connectDataCell };
}
