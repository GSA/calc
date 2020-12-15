import PropTypes from 'prop-types';
import React from 'react';

export default function DescriptionFilter({
  extraClassName,
  label,
  children,
}) {
  let className = 'filter';

  if (extraClassName) {
    className += ` ${extraClassName}`;
  }

  return (
    <span className={className}>
      {label ? `${label}: ` : null}
      <b>
        {children}
      </b>
    </span>
  );
}

DescriptionFilter.propTypes = {
  extraClassName: PropTypes.string,
  label: PropTypes.string,
  children: PropTypes.any.isRequired,
};

DescriptionFilter.defaultProps = {
  extraClassName: null,
  label: null,
};
