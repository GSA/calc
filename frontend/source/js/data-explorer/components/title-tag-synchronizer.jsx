/* global window */

import PropTypes from 'prop-types';

import React from 'react';
import { connect } from 'react-redux';

import { stripTrailingComma } from '../util';

export class TitleTagSynchronizer extends React.Component {
  componentDidMount() {
    this.originalTitle = this.props.document.title;
    this.synchronize();
  }

  componentDidUpdate(prevProps) {
    if (prevProps.q !== this.props.q) {
      this.synchronize();
    }
  }

  componentWillUnmount() {
    this.props.document.title = this.originalTitle;
  }

  synchronize() {
    const q = stripTrailingComma(this.props.q);

    if (q) {
      this.props.document.title = `${q} - CALC Search`;
    } else {
      this.props.document.title = this.originalTitle;
    }
  }

  render() {
    return null;
  }
}

TitleTagSynchronizer.propTypes = {
  q: PropTypes.string.isRequired,
  document: PropTypes.object,
};

TitleTagSynchronizer.defaultProps = {
  document: window.document,
};

export default connect(
  state => ({ q: state.q }),
)(TitleTagSynchronizer);
