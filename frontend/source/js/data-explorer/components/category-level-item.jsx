import PropTypes from 'prop-types';
import React from 'react';

import { autobind } from '../util';

export default class CategoryLevelItem extends React.Component {
  constructor(props) {
    super(props);
    autobind(this, ['_onClick']);
  }

  _onClick(e) {
    this.props.onCheckboxClick(e.target.id, this.props.value, e.target.checked);
  }

  render() {
    return (
      <li>
        <input
          id={this.props.id}
          type="checkbox"
          value={this.props.value.id}
          checked={this.props.checked}
          onChange={(e) => { this._onClick(e); }}
          name="categories"
        />
        <label htmlFor={this.props.id}>
          {this.props.value.title}
        </label>
      </li>
    );
  }
}

CategoryLevelItem.propTypes = {
  id: PropTypes.string.isRequired,
  value: PropTypes.object.isRequired,
  checked: PropTypes.bool.isRequired,
  onCheckboxClick: PropTypes.func.isRequired,
};
