import PropTypes from 'prop-types';
import React from 'react';
import { connect } from 'react-redux';

// import * as autocomplete from '../keyword_autocomplete';
import { setQuery } from '../actions';

import {
  // QUERY_BY_SCHEDULE,
  // QUERY_BY_CONTRACT,
  // QUERY_BY_VENDOR,
  MAX_QUERY_LENGTH
} from '../constants';

import {
  autobind,
  handleEnter,
} from '../util';

export class KeywordFilter extends React.Component {
  constructor(props) {
    super(props);
    this.state = { 
      value: this.props.query,
      keywordDisabled: true,
      keywordValue: "",
      resetFilter: false
    };
    autobind(this, ['handleChange', 'handleEnter']);
  }

  componentWillReceiveProps(nextProps) {
    this.setState({ 
      keywordDisabled: nextProps.keywordDisabled,
      resetFilter: nextProps.resetFilter,
    },
    () => {
      if (this.state.resetFilter) {
        this.setState({ keywordValue: "" });
      }
    });
  }

  // sendDataBack(searchkeyword) {
  //   this.props.parentCallback(searchkeyword);
  // }

  handleChange(e) {
    this.setState({ value: e.target.value, keywordValue: e.target.value });
  }
  

  handleEnter() {
    if (this.state.value !== this.props.query) {
      const qry = `${this.props.laborTyped}|${this.state.value}`;
      this.props.setQuery(qry);
    }
  }

  render() {
    const id = `${this.props.idPrefix}keywords`;
    const placeholder = "Type keywords or certifications or description";

    return (
      <div className="search-group">
        <label htmlFor={id} className="usa-sr-only">
          { placeholder }
        </label>
        <input
          id={id}
          name="keyword"
          value={this.state.keywordValue}
          disabled={this.state.keywordDisabled}
          placeholder={placeholder}
          type="text"
          className="form__inline form__block_control"
          ref={(el) => { this.inputEl = el; }}
          style={{ borderEndWidth: 1, borderEndColor: "#f00" }}
          onChange={this.handleChange}
          onFocus={this.handleFocus}
          onKeyDown={handleEnter(this.handleEnter)}
          maxLength={MAX_QUERY_LENGTH}
          
        />
        {this.props.children}
      </div>
    );
  }
}

KeywordFilter.propTypes = {
  idPrefix: PropTypes.string,
  keywordDisabled: PropTypes.any.isRequired,
  resetFilter: PropTypes.any.isRequired,
  laborTyped: PropTypes.any.isRequired,
  query: PropTypes.string.isRequired,
  // queryType: PropTypes.string.isRequired,
  // queryBy: PropTypes.string,
  setQuery: PropTypes.func.isRequired,
  // api: PropTypes.object.isRequired,
  children: PropTypes.any,
};

KeywordFilter.defaultProps = {
  idPrefix: '',
  children: null,
  // queryBy: QUERY_BY_SCHEDULE,
};

export default connect(
  state => ({
    query: state.q,
    queryType: state.query_type,
    queryBy: state.query_by,
  }),
  { setQuery },
)(KeywordFilter);
