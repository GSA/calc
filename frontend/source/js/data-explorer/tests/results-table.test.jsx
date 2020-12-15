import React from 'react';

import { ResultsTable } from '../components/results-table';
import * as EducationColumn from '../components/results-table/education-column';
import * as ExperienceColumn from '../components/results-table/experience-column';
import makeSetup from './testSetup';

// We need this to avoid a validateDOMNesting warning.
const createDataCell = (Component, props) => (
  <table>
    <tbody>
      <tr>
        <Component {...props} />
      </tr>
    </tbody>
  </table>
);

const makeDataCellSetup = (column, defaultProps) => makeSetup(
  column.DataCell.WrappedComponent, defaultProps, {
    createElement: createDataCell,
  },
);

describe('<ResultsTable>', () => {
  const setup = makeSetup(ResultsTable, {
    sort: { key: 'current_price', descending: false },
    setSort() {},
    results: [],
    contractYear: 'current',
  }, { wrapperOnly: true });

  it('filters out rows with null prices', () => {
    const { wrapper } = setup({
      results: [
        { id: 1, current_price: null },
        { id: 2, current_price: 1 },
      ],
    });

    expect(wrapper.find('tbody tr').length).toBe(1);
  });
});

describe('<EducationColumn.DataCell>', () => {
  const setup = makeDataCellSetup(EducationColumn);

  it('contains the value when value is non-empty', () => {
    const { mounted } = setup({ value: 'High School' });
    expect(mounted.text()).toBe('High School');
  });

  it('contains "N/A" when value is empty', () => {
    const { mounted } = setup({ value: '' });
    expect(mounted.text()).toBe('N/A');
  });
});

describe('<ExperienceColumn.DataCell>', () => {
  const setup = makeDataCellSetup(ExperienceColumn);

  it('is singular when value is 1', () => {
    const { mounted } = setup({ value: 1 });
    expect(mounted.text()).toBe('1 year');
  });

  it('is plural when value is greater than 1', () => {
    const { mounted } = setup({ value: 2 });
    expect(mounted.text()).toBe('2 years');
  });
});
