import React from 'react';

import createSortableColumn from './sortable-column';

const DOCUMENT_SVG = (
  <svg className="document-icon" width="11" height="13" viewBox="0 0 11 13">
    <path d="M2.8501,8.8497 L7.3501,8.8497" id="Stroke-1" stroke="#0770B5" strokeWidth="1" strokeLinecap="round" strokeLinejoin="round" />
    <path d="M2.8501,6.8497 L7.3501,6.8497" id="Stroke-2" stroke="#0770B5" strokeWidth="1" strokeLinecap="round" strokeLinejoin="round" />
    <path d="M2.8501,4.8497 L4.2671,4.8497" id="Stroke-3" stroke="#0770B5" strokeWidth="1" strokeLinecap="round" strokeLinejoin="round" />
    <path d="M9.4492,0 L6.0752,0 C5.4062,0 5.0712,0.809 5.5442,1.281 L6.1702,1.907 L5.3672,2.711 C5.0482,3.03 5.0482,3.548 5.3672,3.867 L6.3322,4.832 C6.6512,5.151 7.1692,5.151 7.4882,4.832 L8.2912,4.028 L8.9182,4.655 C9.3912,5.129 10.2002,4.794 10.2002,4.125 L10.2002,0.751 C10.2002,0.336 9.8642,0 9.4492,0" id="Fill-4" fill="#0770B5" fillRule="evenodd" />
    <path d="M9,5.6553 L9,9.6833 C9,10.4093 8.41,11.0003 7.684,11.0003 L2.517,11.0003 C1.791,11.0003 1.2,10.4093 1.2,9.6833 L1.2,2.5153 C1.2,1.7903 1.791,1.1993 2.517,1.1993 L4.544,1.1993 L4.544,0.0003 L2.517,0.0003 C1.129,0.0003 0,1.1283 0,2.5153 L0,9.6833 C0,11.0713 1.129,12.1993 2.517,12.1993 L7.684,12.1993 C9.071,12.1993 10.2,11.0713 10.2,9.6833 L10.2,5.6553 L9,5.6553 Z" id="Fill-7" fill="#0770B5" fillRule="evenodd" />
  </svg>
);

const column = createSortableColumn({
  key: 'vendor_name',
  title: 'Vendor / Contract',
});

export const { HeaderCell } = column;

function createGsaAdvantageUrl(contractNumber) {
  const id = contractNumber.split('-').join('');

  return `https://www.gsaadvantage.gov/ref_text/${id}/${id}_online.htm`;
}
export const DataCell = column.connectDataCell(
  ({ className, value, result }) => (
    <td className={className}>
      {value}
      <a target="_blank" rel="noopener noreferrer" href={createGsaAdvantageUrl(result.idv_piid)}>
        {result.idv_piid}
        {' '}
        {DOCUMENT_SVG}
      </a>
    </td>
  )
);
