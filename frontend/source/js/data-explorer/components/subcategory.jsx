import PropTypes from 'prop-types';
import React from 'react';

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


async function SubCategory({ idPrefix, category, setCategory }) {
  const categoryid = `${idPrefix}category`;
  const handleChange = (e) => { setCategory(e.target.value); };

  const categorydata = await fetch('https://solutionsid.app.cloud.gov/api/v1/schedule_subcategory?token=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpZCI6OCwiZXhwIjoxNjAzNTcyMjI2fQ.xWT47PaRGgiME5RvUfCKZbGSmGu8oJws7cGwVmAumJg');
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
  //  console.log('Category lable test is this ' +CATEGORY_LABEL);
  //  console.log(categoryposts[0]);

  return (
    <div className="filter filter-category">
      <label htmlFor={categoryid}>
          SubCategory:
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
export default asyncReactor(SubCategory, Loader);
SubCategory.propTypes = {
  category: PropTypes.string.isRequired,
  setCategory: PropTypes.func.isRequired,
  idPrefix: PropTypes.string,
};

SubCategory.defaultProps = {
  idPrefix: '',
};
