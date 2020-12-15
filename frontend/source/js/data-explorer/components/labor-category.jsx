import PropTypes from 'prop-types';
import React from 'react';
import { connect } from 'react-redux';

import * as autocomplete from '../autocomplete';
import { setQuery } from '../actions';

import {
  QUERY_BY_SCHEDULE,
  QUERY_BY_CONTRACT,
  QUERY_BY_VENDOR,
  MAX_QUERY_LENGTH
} from '../constants';

import {
  autobind,
  handleEnter,
} from '../util';

export class LaborCategory extends React.Component {
  constructor(props) {
    super(props);
    this.state = { 
      value: this.props.query
    };

    autobind(this, ['handleChange', 'handleEnter']);
    this.sendDataBack = this.sendDataBack.bind(this);
  }

  componentDidMount() {    
    autocomplete.initialize(this.inputEl, {
      api: this.props.api,
      getQueryType: () => this.props.queryType,
      setFieldValue: (value) => {
        const qry = `${value}|${this.props.search_keywords}`;
        this.props.setQuery(qry);
      },
    });
  }
  
  componentWillReceiveProps(nextProps) {
    if (nextProps.query !== this.props.query) {
      const labAndKeyArr = nextProps.query.split("|");
      this.setState({ value: labAndKeyArr[0] });
      this.sendDataBack(labAndKeyArr[0]);
    }
  }

  componentWillUnmount() {
    autocomplete.destroy(this.inputEl);
  }

  sendDataBack(laborkeyword) {
    this.props.parentCallback(laborkeyword);
  }

  handleChange(e) {
    const labAndKeyArr = e.target.value.split("|");
    this.setState({ value: labAndKeyArr[0] });
    this.sendDataBack(e.target.value);  
  }

  handleEnter() {
    if (this.state.value !== this.props.query) { // WORK
      const qry = `${this.state.value}|${this.props.search_keywords}`;
      this.props.setQuery(qry);
      this.sendDataBack(this.state.value);
    }
  }

  render() {
    const id = `${this.props.idPrefix}labor_category`;
    let placeholder = "Type a labor category*";

    if (this.props.queryBy === QUERY_BY_CONTRACT) {
      placeholder = "Type a contract number";
    } else if (this.props.queryBy === QUERY_BY_VENDOR) {
      placeholder = "Type a vendor name";
    }

    return (
      <div className="search-group">
        <label htmlFor={id} className="usa-sr-only">
          { placeholder }
        </label>
        <input
          id={id}
          name="q"
          placeholder={placeholder}
          type="text"
          className="form__inline form__block_control"
          ref={(el) => { this.inputEl = el; }}
          value={this.state.value}
          onChange={this.handleChange}
          onKeyDown={handleEnter(this.handleEnter)}
          maxLength={MAX_QUERY_LENGTH}
        />
        {this.props.children}
      </div>
    );
  }
}

LaborCategory.propTypes = {
  idPrefix: PropTypes.string,
  query: PropTypes.string.isRequired,
  queryType: PropTypes.string.isRequired,
  queryBy: PropTypes.string,
  setQuery: PropTypes.func.isRequired,
  search_keywords: PropTypes.string,
  api: PropTypes.object.isRequired,
  children: PropTypes.any,
  parentCallback: PropTypes.any
};

LaborCategory.defaultProps = {
  idPrefix: '',
  children: null,
  queryBy: QUERY_BY_SCHEDULE,
  parentCallback: (''),
  search_keywords: ''
};

export default connect(
  state => ({
    query: state.q,
    queryType: state.query_type,
    queryBy: state.query_by,
  }),
  { setQuery },
)(LaborCategory);
