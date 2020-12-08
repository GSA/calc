/* eslint-disable no-unused-vars */

import React from 'react';
import { connect } from 'react-redux';

/* global $ */

import PropTypes from 'prop-types';

import { Range } from 'rc-slider';

import {
  setExperience,
} from '../actions';

import {
  autobind,
  filterActive,
} from '../util';

import {
  MIN_EXPERIENCE,
  MAX_EXPERIENCE,
} from '../constants';

function makeOptions(min, max) {
  const options = [];

  for (let i = min; i <= max; i++) {
    options.push(
      <option key={i} value={i}>
        {i}
      </option>
    );
  }

  return options;
}

export class Experience extends React.Component {
  constructor(props) {
    super(props);
    autobind(this, ['onSliderChange', 'onAfterSliderChange']);
    this.state = {
      sliderVal: [this.props.min, this.props.max],
    };
  }

  componentWillReceiveProps(newProps) {
    const [min, max] = this.state.sliderVal;
    if (min !== newProps.min || max !== newProps.max) {
      this.setState({ sliderVal: [newProps.min, newProps.max] });
    }
  }

  onSliderChange(val) {
    this.setState({ sliderVal: val });
  }

  onAfterSliderChange(val) {
    const [min, max] = val;
    if (min !== this.props.min) {
      this.props.setExperience('min', min);
    }
    if (max !== this.props.max) {
      this.props.setExperience('max', max);
    }
  }

  render() {
    const [min, max] = this.state.sliderVal;

    const rangeId = `${this.props.idPrefix}range`;
    const minId = `${this.props.idPrefix}min`;
    const maxId = `${this.props.idPrefix}max`;
    const baseClasses = 'select-small';
    const minClasses = filterActive(min !== MIN_EXPERIENCE, baseClasses);
    const maxClasses = filterActive(max !== MAX_EXPERIENCE, baseClasses);

    const onChange = type => (e) => {
      this.props.setExperience(type, parseInt(e.target.value, 10));
    };

    return (
      <div className="filter" ref={(el) => { this.rootEl = el; }}>
        <fieldset>
          <legend>
            Experience:
          </legend>
          <Range
            id={rangeId}
            allowCross={false}
            min={MIN_EXPERIENCE}
            max={MAX_EXPERIENCE}
            value={this.state.sliderVal}
            onChange={this.onSliderChange}
            onAfterChange={this.onAfterSliderChange}
            className="experience-slider"
          />
          <div className="experience_range">
            <label htmlFor={minId} className="usa-sr-only">
              Minimum Years
            </label>
            <select
              id={minId}
              value={min}
              name="min_experience"
              onChange={onChange('min')}
              className={minClasses}
            >
              {makeOptions(MIN_EXPERIENCE, max)}
            </select>
            {' - '}
            <label htmlFor={maxId} className="usa-sr-only">
              Maximum Years
            </label>
            <select
              id={maxId}
              value={max}
              name="max_experience"
              onChange={onChange('max')}
              className={maxClasses}
            >
              {makeOptions(min, MAX_EXPERIENCE)}
            </select>
            {' years'}
          </div>
        </fieldset>
      </div>
    );
  }
}

Experience.propTypes = {
  min: PropTypes.number.isRequired,
  max: PropTypes.number.isRequired,
  setExperience: PropTypes.func.isRequired,
  idPrefix: PropTypes.string,
};

Experience.defaultProps = {
  idPrefix: 'experience-',
};

export default connect(
  state => ({
    min: state.min_experience,
    max: state.max_experience,
  }),
  { setExperience },
)(Experience);
