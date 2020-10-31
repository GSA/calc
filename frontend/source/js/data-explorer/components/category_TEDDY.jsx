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
    <h2>Loading <br />Categories...</h2>
  );
}


async function Category({ idPrefix, category, setCategory }) {
  const categoryid = `${idPrefix}category`;
  // const handleChange = (e) => { setCategory(e.target.value); };
    const handleChange = (e) => { setSinNumber(e.target.value); };

  const categorydata = await fetch('https://solutionsid.app.cloud.gov/api/v1/prmthd');
  const categoryposts = await categorydata.json();

  let CATEGORY_LABEL = "";
  let i = 0;

  categoryposts[0].forEach((categories) => {
    if (i === categoryposts[0].length - 1) {
      CATEGORY_LABEL += "\"".concat(categories.title.concat("\":\"".concat(categories.title.concat("\" "))));
      CATEGORY_ID += "\"".categories.id."\" ";
      // console.log(CATEGORY_ID);
    } else {
      CATEGORY_LABEL += "\"".concat(categories.title.concat("\":\"".concat(categories.title.concat("\", "))));
      CATEGORY_ID += "\"".categories.id."\", ";
      console.log(CATEGORY_ID);
    }
    i++;
  });
  console.log(jsonify(CATEGORY_LABEL));
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
        value={"444"}
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
  sinNumber: PropTypes.string.isRequired,
  setSinNumber: PropTypes.func.isRequired,
  idPrefix: PropTypes.string,
};
//setCategory: PropTypes.func.isRequired,
Category.defaultProps = {
  idPrefix: '',
};

export default connect(
  state => ({ sinNumber: state.sinNumber })
)(Sinnumber);
