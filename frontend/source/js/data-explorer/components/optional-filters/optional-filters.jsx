import React, { Fragment } from 'react';

import BusinessSize from '../business-size';
import ContractYear from '../contract-year';
import EducationLevel from '../education-level';
import Experience from '../experience';
import SecurityClearence from '../security-clearence';
import SinNumber from '../sin-number';
import Site from '../site';

const OptionalFilters = () => (
  <Fragment>
    <EducationLevel />
    <Experience />
    <Site />
    <BusinessSize />
    <SecurityClearence />
    <SinNumber />
    <ContractYear />
  </Fragment>
);

export default OptionalFilters;
