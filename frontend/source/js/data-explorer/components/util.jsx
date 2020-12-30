import React from 'react';

export function makeOptions(labels, defaultMsg = '(all)') {
  return [
    { key: '', value: '', label: defaultMsg },
  ].concat(Object.keys(labels).map(
    value => ({ value, label: labels[value] }),
  )).map(({ value, label }) => (
    <option key={value} value={value}>
      {label}
    </option>
  ));
}

export function makeCategoryOptions(labels, defaultMsg = '(all)') {
  return [
    { key: '', value: '', label: defaultMsg },
  ].concat(Object.keys(labels).map(
    value => ({ value, label: labels[value] }),
  )).map(({ value, label }) => (
    <option key={value} value={value}>
      {label}
    </option>
  ));
}

// https://facebook.github.io/react/docs/animation.html#rendering-a-single-child
export function FirstChild(props) {
  const childrenArray = React.Children.toArray(props.children);

  return childrenArray[0] || null;
}
