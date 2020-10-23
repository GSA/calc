import React from 'react';
import PropTypes from 'prop-types';
import Loadable from 'react-loadable';

export const Loading = ({ error, pastDelay }) => {
  if (error) {
    return (
      <div className="usa-alert usa-alert-error" role="alert">
        <h4>
          Oops!
        </h4>
        <p>
          Error loading component. Try refreshing the page.
        </p>
      </div>
    );
  } if (pastDelay) {
    return (
      <div>
        Loading...
      </div>
    );
  }
  // default to an empty loading component
  return null;
};

Loading.propTypes = {
  error: PropTypes.object,
  pastDelay: PropTypes.bool.isRequired,
};

Loading.defaultProps = {
  error: null,
};

export default function LoadableWrapper(loader, opts) {
  /* `loader` should be an anonymous function that `import`s
   * the path to the component to be loaded.
   * The internal path must be relative to the actual component,
   * not to LoadableWrapper.
   *
   * For example:
   * ```
   * const LoadableWidget = LoadableWrapper(
   *   () => import('./widget'));
   *
   * Additional options can be passed via the `opts` object.
   * See https://github.com/jamiebuilds/react-loadable#loadable-and-loadablemap-options
   * for documentation on available options.
   */
  return Loadable(Object.assign({
    loader,
    loading: Loading,
    delay: 300,
  }, opts));
}
