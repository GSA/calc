import PropTypes from 'prop-types';
import React from 'react';
import { connect } from 'react-redux';

import { setSort } from '../../actions';
import createSortableColumn from './sortable-column';
import * as ExcludedColumn from './excluded-column';
import * as LaborCategoryColumn from './labor-category-column';
import * as EducationColumn from './education-column';
import * as KeywordsColumn from './keywords-column';
import * as CertificationsColumn from './certifications-columns';
import * as ExperienceColumn from './experience-column';
import * as PriceColumn from './price-column';
import * as VendorColumn from './vendor';

const COLUMNS = [
  ExcludedColumn,
  LaborCategoryColumn,
  PriceColumn,
  EducationColumn,
  ExperienceColumn,
  VendorColumn,
  KeywordsColumn,
  CertificationsColumn,
  createSortableColumn({
    key: 'schedule',
    title: 'Contract vehicle',
  }),
];

const { priceForContractYear } = PriceColumn;

export class ResultsTable extends React.Component {

  constructor(props) {
    super(props);
    this.state = { 
      search_keywords:"",
      search_filter_need : false
     };
  }

  componentWillReceiveProps(nextProps) {
    this.setState({ search_keywords: nextProps.search_keywords });
    if(nextProps.search_keywords.length > 2){
      this.setState({ search_filter_need: true });
    }else{
      this.setState({ search_filter_need: false });
    }
  }

  checkKeywordOrCertificationExist(searchStr,data){
    let search_arr = searchStr.split(',')
    let noMatchFound = true
    let i=0
    for(i=0;i<search_arr.length;i++){
      if ((data.toLowerCase()).indexOf(search_arr[i].toLowerCase()) != -1 ){
        noMatchFound = false
      }
    }
    
    return noMatchFound
  }

  renderBodyRows() {
    return this.props.results
      .filter(r => !!priceForContractYear(this.props.contractYear, r))
      .map(result => (
        <tr 
        key={result.id} 
        className={
          (
            (
              (!(result.keywords) || this.checkKeywordOrCertificationExist(this.state.search_keywords,result.keywords))
                 &&	
              (!(result.certifications) || this.checkKeywordOrCertificationExist(this.state.search_keywords,result.certifications) )
            ) && this.state.search_filter_need ? 'hidden' : ''
          )
        }>
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
