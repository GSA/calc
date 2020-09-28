import React, { Fragment } from 'react';

import BusinessSize from '../business-size';
import Category from '../category';
import ContractYear from '../contract-year';
import EducationLevel from '../education-level';
import Experience from '../experience';
import SecurityClearence from '../security-clearence';
import SinNumber from '../sin-number';
import Site from '../site';
//  import category from '../category';
import Subcategory from '../Subcategory';

const OptionalFilters = () => (
  <Fragment>
    <EducationLevel />
    <Experience />
    <Site />
    <BusinessSize />
    <Category />
    <Subcategory />
    <SecurityClearence />
    <SinNumber />
    <ContractYear />
  </Fragment>
);

export default OptionalFilters;
