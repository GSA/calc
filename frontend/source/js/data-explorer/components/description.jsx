import PropTypes from 'prop-types';
import React from 'react';
import { connect } from 'react-redux';

import DescriptionFilter from './description-filter';

import {
  MIN_EXPERIENCE,
  MAX_EXPERIENCE,
  EDU_LABELS,
  SITE_LABELS,
  BUSINESS_SIZE_LABELS,
} from '../constants';

import { scheduleLabels } from '../schedule-metadata';

import { formatCommas, stripTrailingComma } from '../util';

export function Description({
  shownResults,
  totalResults,
  minExperience,
  maxExperience,
  education,
  site,
  businessSize,
  schedule,
  laborCategory,
}) {
  let results = ' results ';
  const laborCategories = [];
  const filtersClasses = ['filters'];
  const filters = [];

  if (laborCategory) {
    const laborCategoryArr = laborCategory.split('|');
    [laborCategory] = laborCategoryArr;
    laborCategories.push(
      <DescriptionFilter key="lab">
        {stripTrailingComma(laborCategory)}
      </DescriptionFilter>,
    );
  }

  if (education.length) {
    filters.push(
      <DescriptionFilter
        key="edu"
        label="education level"
        extraClassName="education-filter"
      >
        {education.map(x => EDU_LABELS[x]).join(', ')}
      </DescriptionFilter>,
    );
  }

  if (minExperience !== MIN_EXPERIENCE
      || maxExperience !== MAX_EXPERIENCE) {
    filters.push(
      <DescriptionFilter key="exp" label="experience">
        {minExperience}
        {' '}
-
        {maxExperience}
        {' '}
years
      </DescriptionFilter>,
    );
  }

  if (site) {
    filters.push(
      <DescriptionFilter key="sit" label="worksite">
        {SITE_LABELS[site]}
      </DescriptionFilter>,
    );
  }

  if (businessSize) {
    filters.push(
      <DescriptionFilter key="bus" label="business size">
        {BUSINESS_SIZE_LABELS[businessSize]}
      </DescriptionFilter>,
    );
  }

  if (schedule) {
    filters.push(
      <DescriptionFilter key="sch" label="schedule">
        {scheduleLabels[schedule]}
      </DescriptionFilter>,
    );
  }

  if (filters.length) {
    results += 'with ';
  } else {
    filtersClasses.push('hidden');
  }


  return (   
    <div id="description">
      <h4>
        Hourly rate data
        <span>
          { laborCategories.length ? ' for ' : '' }
        </span>
        { laborCategories }
      </h4>
      <p>
        { shownResults === totalResults ? '' : `Showing ${formatCommas(shownResults)} of ` }
        <span className="total">
          {formatCommas(totalResults)}
        </span>
        {results}

        <span className={filtersClasses.join(' ')}>
          {filters}
        </span>
      </p>
    </div>
  );
}

Description.propTypes = {
  shownResults: PropTypes.number.isRequired,
  totalResults: PropTypes.number.isRequired,
  minExperience: PropTypes.number.isRequired,
  maxExperience: PropTypes.number.isRequired,
  education: PropTypes.array.isRequired,
  site: PropTypes.string.isRequired,
  businessSize: PropTypes.string.isRequired,
  schedule: PropTypes.string.isRequired,
  laborCategory: PropTypes.string.isRequired,
};

function mapStateToProps(state) {
  return {
    shownResults: state.rates.data.results.length,
    totalResults: state.rates.data.count,
    minExperience: state.min_experience,
    maxExperience: state.max_experience,
    education: state.education,
    site: state.site,
    businessSize: state.business_size,
    schedule: state.schedule,
    laborCategory: state.q,
  };
}

export default connect(mapStateToProps)(Description);
