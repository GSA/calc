import PropTypes from 'prop-types';
import React from 'react';

import { autobind } from '../util';
import { CAT_LABELS } from '../constants';

export default class CategoryLevelItem extends React.Component {
  constructor(props) {
    super(props);
    autobind(this, ['_onClick']);
  }

  _onClick() {
    // console.log("CLICKKKKKED CAT" + this.props.checked);
    this.props.onCheckboxClick(this.props.value);
  }

  render() {
    console.log("RENDERRRRRRRIINNNNG" + JSON.stringify(this.props));
    //console.log("PROPS: " + this.props.value.id + " - " + this.props.checked);
    return (
      <li>
        <input
          id={this.props.id}
          type="checkbox"
          value={this.props.value.id}
          checked={this.props.checked}
          onChange={this._onClick}
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
  value: PropTypes.string.isRequired,
  checked: PropTypes.bool.isRequired,
  onCheckboxClick: PropTypes.func.isRequired,
};
