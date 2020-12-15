import PropTypes from 'prop-types';
import React from 'react';
import { connect } from 'react-redux';

export function LoadingIndicator({ error, inProgress }) {
  let errorMessage = null;
  let ariaStatus = inProgress ? 'Loading results' : 'Results loaded.';

  if (error) {
    ariaStatus = '';
    if (error !== 'abort') {
      errorMessage = (
        <div className="error-message">
          {error}
        </div>
      );
      ariaStatus = `An error occurred when loading results: ${error}`;
    }
  }

  return (
    <div>
      {/* Note that in order for this aria-live region to work
        * across most screen readers, it needs to be in the DOM
        * on page load! */}
      <div className="usa-sr-only" role="status" aria-live="polite">
        {ariaStatus}
      </div>
      {/* CSS for the following element was originally designed with
        * only sighted users in mind, which is why we're hiding it
        * from screen readers and using the preceding element to
        * convey status information to visually impaired users. */}
      <div className="loading-indicator" aria-hidden="true">
        <p className="message">
          Loading results...
        </p>
        {errorMessage}
      </div>
    </div>
  );
}

LoadingIndicator.propTypes = {
  error: PropTypes.string,
  inProgress: PropTypes.bool.isRequired,
};

LoadingIndicator.defaultProps = {
  error: null,
};

export default connect(
  state => ({
    error: state.rates.error,
    inProgress: state.rates.inProgress,
  }),
)(LoadingIndicator);
