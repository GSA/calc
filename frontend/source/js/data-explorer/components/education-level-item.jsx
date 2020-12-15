import PropTypes from 'prop-types';
import React from 'react';

import { autobind } from '../util';
import { EDU_LABELS } from '../constants';

export default class EducationLevelItem extends React.Component {
  constructor(props) {
    super(props);
    autobind(this, ['_onClick']);
  }

  _onClick() {
    this.props.onCheckboxClick(this.props.value);
  }

  render() {
    return (
      <li>
        <input
          id={this.props.id}
          type="checkbox"
          value={this.props.value}
          checked={this.props.checked}
          onChange={this._onClick}
          name="education"
        />
        <label htmlFor={this.props.id}>
          {EDU_LABELS[this.props.value]}
        </label>
      </li>
    );
  }
}

EducationLevelItem.propTypes = {
  id: PropTypes.string.isRequired,
  value: PropTypes.string.isRequired,
  checked: PropTypes.bool.isRequired,
  onCheckboxClick: PropTypes.func.isRequired,
};
