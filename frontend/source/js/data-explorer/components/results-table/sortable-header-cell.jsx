import PropTypes from 'prop-types';
import React from 'react';
import classNames from 'classnames';

import { handleEnterOrSpace } from '../../util';
import Tooltip from '../tooltip';

const createSortToggler = (key, sort, setSort) => () => {
  let descending = false;

  if (sort.key === key && !sort.descending) {
    descending = true;
  }

  setSort({
    key,
    descending,
  });
};

const createSortHeaderTooltip = (title, { sorted, descending }) => {
  if (!sorted) {
    return `${title}: select to sort ascending`;
  }

  if (descending) {
    return `${title}: sorted descending, select to sort ascending`;
  }

  return `${title}: sorted ascending, select to sort descending`;
};

const getHeaderCellClasses = (key, sort) => ({
  sortable: true,
  sorted: sort.key === key,
  ascending: sort.key === key && !sort.descending,
  descending: sort.key === key && sort.descending,
  [`column-${key}`]: true,
});

export function createHeaderCellConnector(description, title, key) {
  return (Component) => {
    const wrappedComponent = ({ sort, setSort }) => {
      const classes = getHeaderCellClasses(key, sort);

      return (
        <Component
          className={classNames(classes)}
          toggleSort={createSortToggler(key, sort, setSort)}
          tooltip={createSortHeaderTooltip(description || title,
            classes)}
          title={title}
        />
      );
    };

    wrappedComponent.propTypes = {
      sort: PropTypes.object.isRequired,
      setSort: PropTypes.func.isRequired,
    };

    return wrappedComponent;
  };
}

export class GenericHeaderCell extends React.Component {
  constructor(props) {
    super(props);
    this.state = { focused: false };
  }

  render() {
    return (
      <th // eslint-disable-line jsx-a11y/no-static-element-interactions
        scope="col"
        onFocus={() => { this.setState({ focused: true }); }}
        onBlur={() => { this.setState({ focused: false }); }}
        tabIndex="0"
        role="button"
        aria-label={this.props.tooltip}
        className={this.props.className}
        onKeyDown={handleEnterOrSpace(this.props.toggleSort)}
        onClick={this.props.toggleSort}
      >
        <Tooltip text={this.props.tooltip} show={this.state.focused}>
          {this.props.title}
        </Tooltip>
      </th>
    );
  }
}

GenericHeaderCell.propTypes = {
  className: PropTypes.string.isRequired,
  title: PropTypes.string.isRequired,
  tooltip: PropTypes.string.isRequired,
  toggleSort: PropTypes.func.isRequired,
};
