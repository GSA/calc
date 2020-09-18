import PropTypes from 'prop-types';
import React from 'react';
import { connect } from 'react-redux';
import {asyncReactor} from 'async-reactor';

import { filterActive } from '../util';
import { makeOptions } from './util';
import { setBusinessSize as setBusinessSizeAction } from '../actions';
import { BUSINESS_SIZE_LABELS } from '../constants';

function Loader() {

  return (
    <h2>Loading ...</h2>
  );
}


async function BusinessSize({ idPrefix,size, setSize }) {

  const id = `${idPrefix}category`;
  const handleChange = (e) => { setSize(e.target.value); };

  const data = await fetch('https://cors-anywhere.herokuapp.com/https://solutionsid.app.cloud.gov/api/v1/schedule_category?token=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpZCI6NSwiZXhwIjoxNjAwNTI0Mjc5fQ.esHBHJHwFJ3nymQJrPm8G0o1y2W2qeJNP_0Q43nkgXs');
  const posts = await data.json();

  let CATEGORY_LABEL="";
  let i=0;

  posts[0].forEach(categories => {
    if (i == posts[0].length - 1) {
      CATEGORY_LABEL+="\""+categories.title+"\":\""+categories.title +"\" ";
    }else{
    CATEGORY_LABEL+="\""+categories.title+"\":\""+categories.title +"\", ";
    }
    i++;
  });
  CATEGORY_LABEL=JSON.parse('{'+CATEGORY_LABEL+'}');
  console.log(CATEGORY_LABEL);
  console.log(posts[0]);

  return (
    <div className="filter filter-business_size">
      <label htmlFor={id}>
          Category:
      </label>
      <select
        id={id}
        name="business_size"
        value={size}
        onChange={handleChange}
        className={filterActive(size !== '')}
      >
        {makeOptions(CATEGORY_LABEL)}
      </select>
    </div>
  );
}
export default asyncReactor(BusinessSize, Loader);
BusinessSize.propTypes = {
  size: PropTypes.string.isRequired,
  setSize: PropTypes.func.isRequired,
  idPrefix: PropTypes.string,
};

BusinessSize.defaultProps = {
  idPrefix: '',
};

// const mapStateToProps = (state) => {
//   return {
//       // will be available as props.trips
//       size: state.size
//   }
// }

// const mapDispatchToProps = (dispatch) => {
//   return {
//       // will be available as props.fetch()
//       setSize: () => dispatch(setBusinessSizeAction)
//   }
// }
// export default connect(mapStateToProps,mapDispatchToProps)(asyncReactor);


// export default connect(
//   state => ({ size: state.business_size })
// )(BusinessSize);

