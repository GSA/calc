import PropTypes from 'prop-types';
import React from 'react';

//  import { connect } from 'react-redux';
import { asyncReactor } from 'async-reactor';

import { filterActive } from '../util';
import { makeOptions } from './util';
//  import { setCategory as setCategoryAction } from '../actions';
//  import { setBusinessSize as setBusinessSizeAction } from '../actions';
//  import { BUSINESS_SIZE_LABELS } from '../constants';
const fetch = require("node-fetch");

function Loader() {
  return (
    <h2>Loading...</h2>
  );
}


async function Category({ idPrefix, category, setCategory }) {
  const categoryid = `${idPrefix}category`;
  const handleChange = (e) => { setCategory(e.target.value); };

  const categorydata = await fetch('https://solutionsid.app.cloud.gov/api/v1/schedule_category?token=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpZCI6NSwiZXhwIjoxNjA2MzEzNTQ0fQ.L9OCuCruD8tDdggj-JcC65dkvLkKVBhqUFLeXiwW9Jo');
  const categoryposts = await categorydata.json();

  let CATEGORY_LABEL = "";
  let i = 0;

  categoryposts[0].forEach((categories) => {
    if (i === categoryposts[0].length - 1) {
      CATEGORY_LABEL += "\"".concat(categories.title.concat("\":\"".concat(categories.title.concat("\" "))));
    } else {
      CATEGORY_LABEL += "\"".concat(categories.title.concat("\":\"".concat(categories.title.concat("\", "))));
    }
    i++;
  });
  CATEGORY_LABEL = JSON.parse('{'.concat(CATEGORY_LABEL).concat('}'));
  //    console.log('Category lable test is this '+CATEGORY_LABEL);
  //  console.log(categoryposts[0]);

  return (
    <div className="filter filter-category">
      <label htmlFor={categoryid}>
          Category:
      </label>
      <select
        categoryid={categoryid}
        name="category"
        value={category}
        onChange={handleChange}
        className={filterActive(category !== '')}
      >
        {makeOptions(CATEGORY_LABEL)}
      </select>
      {/* <label htmlFor={categoryid}>
          Sub-Category:
      </label>
      <select
        categoryid={categoryid}
        name="category"
        value={category}
        onChange={handleChange}
        className={filterActive(category !== '')}
      >
        {makeOptions(CATEGORY_LABEL)}
      </select> */}
    </div>
  );
}
export default asyncReactor(Category, Loader);
Category.propTypes = {
  category: PropTypes.string.isRequired,
  setCategory: PropTypes.func.isRequired,
  idPrefix: PropTypes.string,
};

Category.defaultProps = {
  idPrefix: '',
};
