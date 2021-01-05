import LoadableWrapper from '../loadable-wrapper';

const LoadableOptionalFilters = LoadableWrapper(
  () => import('./optional-filters')
);

export default LoadableOptionalFilters;
