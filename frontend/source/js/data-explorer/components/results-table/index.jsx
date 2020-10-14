import PropTypes from 'prop-types';
import React from 'react';
import { connect } from 'react-redux';

import { setSort } from '../../actions';
import createSortableColumn from './sortable-column';
import * as ExcludedColumn from './excluded-column';
import * as LaborCategoryColumn from './labor-category-column';
import * as EducationColumn from './education-column';
import * as ExperienceColumn from './experience-column';
import * as PriceColumn from './price-column';
import * as keyColumn from './keywords-column';
import * as CertColumn from './certifications-columns';
import * as VendorColumn from './vendor';

const COLUMNS = [
  ExcludedColumn,
  LaborCategoryColumn,
  PriceColumn,
  EducationColumn,
  keyColumn,
  CertColumn,
  ExperienceColumn,
  VendorColumn,
  createSortableColumn({
    key: 'schedule',
    title: 'Contract vehicle',
  }),
];

const { priceForContractYear } = PriceColumn;

export class ResultsTable extends React.Component {
  renderBodyRows() {
    return this.props.results
      .filter(r => !!priceForContractYear(this.props.contractYear, r))
      .map(result => (
        <tr key={result.id}>
          {COLUMNS.map((col) => {
            const cellKey = `${result.id}-${col.DataCell.cellKey}`;
            return (
              <col.DataCell key={cellKey} sort={this.props.sort} result={result} />
            );
          })}
        </tr>
      ));
  }

  render() {
    const id = `${this.props.idPrefix}results-table`;
    const idHref = `#${id}`;

    return (
      <table id={id} className="results has-data sortable hoverable">
        <thead>
          <tr>
            {COLUMNS.map(col => (
              <col.HeaderCell
                key={`header-${col.DataCell.cellKey}`}
                setSort={this.props.setSort}
                sort={this.props.sort}
              />
            ))}
          </tr>
        </thead>
        <tbody>
          {this.renderBodyRows()}
        </tbody>
        <tfoot>
          <tr>
            <td colSpan={COLUMNS.length} className="results-table_return-link">
              <a href={idHref}>
Return to the top
              </a>
            </td>
          </tr>
        </tfoot>
      </table>
    );
  }
}

ResultsTable.propTypes = {
  sort: PropTypes.object.isRequired,
  setSort: PropTypes.func.isRequired,
  results: PropTypes.array.isRequired,
  contractYear: PropTypes.string.isRequired,
  idPrefix: PropTypes.string,
};

ResultsTable.defaultProps = {
  idPrefix: '',
};

function mapStateToProps(state) {
  return {
    sort: state.sort,
    results: state.rates.data.results,
    contractYear: state['contract-year'],
  };
}

const mapDispatchToProps = { setSort };

export default connect(mapStateToProps, mapDispatchToProps)(ResultsTable);
