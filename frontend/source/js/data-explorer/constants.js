// @ts-check
/* eslint-disable no-unused-vars */
/* global window */

export const MAX_EXPERIENCE = 45;
export const MIN_EXPERIENCE = 0;

export const HISTOGRAM_BINS = 12;

// TODO: This is duplicated from server-side code; consolidate it.
export const EDU_HIGH_SCHOOL = 'HS';
export const EDU_ASSOCIATES = 'AA';
export const EDU_BACHELORS = 'BA';
export const EDU_MASTERS = 'MA';
export const EDU_PHD = 'PHD';

export const EDU_LABELS = {
  [EDU_HIGH_SCHOOL]: 'High School',
  [EDU_ASSOCIATES]: 'Associates',
  [EDU_BACHELORS]: 'Bachelors Degree',
  [EDU_MASTERS]: 'Masters Degree',
  [EDU_PHD]: 'Ph.D',
};
console.log("EDU_LABELS"+EDU_LABELS.EDU_HIGH_SCHOOL);
/***  CATEGORIES ***/
export const OFFICE_MGMT = '200%2C222';
export const FACILITIES = '17';
export const FURNITURE = '400';
export const HUMAN_CAPITAL = '51 501, 51 504, 51 505, 51 506';

export const CAT_LABELS = {
  [OFFICE_MGMT]: 'Office Management',
  [FACILITIES]: 'Facilities',
  [FURNITURE]: 'Furniture and Furnishings',
  [HUMAN_CAPITAL]: 'Human Capital',
};
//[{"code":"A","id":1,"title":"Office Management"},{"code":"B","id":2,"title":"Facilities"},{"code":"C","id":3,"title":"Furniture and Furnishings"},{"code":"D","id":4,"title":"Human Capital"},{"code":"E","id":5,"title":"Industrial Products and Services"},{"code":"F","id":6,"title":"Information Technology"},{"code":"G","id":7,"title":"Miscellaneous"},{"code":"H","id":8,"title":"Professional Services"},{"code":"I","id":9,"title":"Scientific Management and Solutions"},{"code":"J","id":10,"title":"Security and Protection"},{"code":"K","id":11,"title":"Transportation and Logistics Services"},{"code":"L","id":12,"title":"Travel"}]
const SOLUTIONS_ID_API2 = 'https://solutionsid.app.cloud.gov/api/v1/schedule_cats?token=';
// const SOLUTIONS_ID_API = 'https://solutionsid.app.cloud.gov/api/v1/schedule_category?token=';
const SOLUTIONSID_API_TOKEN2 = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpZCI6NSwiZXhwIjoxNjA2MzEzNTQ0fQ.L9OCuCruD8tDdggj-JcC65dkvLkKVBhqUFLeXiwW9Jo';
var categories;
    fetch(SOLUTIONS_ID_API2 + SOLUTIONSID_API_TOKEN2)
    //fetch(TEST_API)
      .then( (response) => response.json())
      .then(data => categories = data)
      .then(() => console.log("CON1:"+JSON.stringify(categories)))


    /*if (categories !== undefined) {
  console.log("*********************");
  var schCats = categories[0]["scheduleCategories"];
  console.log("CON3"+JSON.stringify(schCats));
} else {
  console.log("UUUUUUUUUUUUUUUUUUUUU");
} */


/*** END CATEGORIES ***/
export const BUSINESS_SIZE_LABELS = {
  s: 'small business',
  o: 'other than small',
};

export const SECURITY_CLEARANCE_LABELS = {
  yes: 'yes',
  no: 'no',
};

export const SITE_LABELS = {
  customer: 'customer',
  contractor: 'contractor',
  both: 'both',
};

export const CONTRACT_YEAR_CURRENT = 'current';
export const CONTRACT_YEAR_1 = '1';
export const CONTRACT_YEAR_2 = '2';

export const CONTRACT_YEAR_LABELS = {
  [CONTRACT_YEAR_CURRENT]: 'Current year',
  [CONTRACT_YEAR_1]: 'One year out',
  [CONTRACT_YEAR_2]: 'Two years out',
};

export const DEFAULT_CONTRACT_YEAR = 'current';

export const EMPTY_RATES_DATA = {
  minimum: 0,
  maximum: 0.001,
  average: 0,
  first_standard_deviation: 0,
  count: 0,
  results: [],
  wage_histogram: [
    { count: 0, min: 0, max: 0 },
  ],
};

export const DEFAULT_SORT = { key: 'current_price', descending: false };

export const SORT_KEYS = [
  'labor_category',
  'education_level',
  'min_years_experience',
  'current_price',
  'idv_piid',
  'vendor_name',
  'schedule',
];

export const QUERY_TYPE_MATCH_ALL = 'match_all';

export const QUERY_TYPE_MATCH_EXACT = 'match_exact';

export const DEFAULT_QUERY_TYPE = QUERY_TYPE_MATCH_ALL;

export const QUERY_TYPE_LABELS = {
  [QUERY_TYPE_MATCH_ALL]: 'Contains words',
  [QUERY_TYPE_MATCH_EXACT]: 'Exact match',
};

export const SIN_NUMBER = {
  sinNumber: '123',
};

export const MAX_QUERY_LENGTH = 255;

export const QUERY_BY_SCHEDULE = '';
export const QUERY_BY_VENDOR = 'vendor_name';
export const QUERY_BY_CONTRACT = 'idv_piid';

export const DEFAULT_QUERY_BY = QUERY_BY_SCHEDULE;

export const SOLUTIONSID_API_TOKEN = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpZCI6NSwiZXhwIjoxNjA2MzEzNTQ0fQ.L9OCuCruD8tDdggj-JcC65dkvLkKVBhqUFLeXiwW9Jo';
