import PropTypes from 'prop-types';
import React from 'react';
import { connect } from 'react-redux';

import { excludeNone } from '../../actions';

function RestoreExcluded({ exclude, onClick }) {
  const len = exclude.length;
  const rows = `row${len === 1 ? '' : 's'}`;
  const handleClick = (e) => {
    e.preventDefault();
    onClick();
  };

  return (
    <a
      className="restore"
      href="?exclude="
      style={len === 0 ? { display: 'none' } : null}
      title={`${rows}: ${exclude.join(', ')}`}
      onClick={handleClick}
    >
      {len > 0 ? `★ Restore ${len} ${rows}` : ''}
    </a>
  );
}

RestoreExcluded.propTypes = {
  exclude: PropTypes.array.isRequired,
  onClick: PropTypes.func.isRequired,
};

function mapStateToProps(state) {
  return {
    exclude: state.exclude,
  };
}

const mapDispatchToProps = {
  onClick: excludeNone,
};

export default connect(mapStateToProps, mapDispatchToProps)(RestoreExcluded);
