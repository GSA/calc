from typing import List, SupportsFloat


def get_histogram(values: List[SupportsFloat], num_bins: int=10) -> List[dict]:
    """
    Get a histogram of a list of numeric values.
    Returns array of "bin" dicts with keys `count`, `max`, and `min`.
    """

    if (num_bins <= 0):
        raise ValueError('num_bins must be greater than 0')

    # convert values to floats
    fvalues = [float(v) for v in values]

    # When input array is empty, can't determine range so use 0.0 - 1.0
    # as numpy.histogram does
    if (len(fvalues) == 0):
        mn, mx = 0.0, 1.0
    else:
        # find the min and max
        mn, mx = min(fvalues), max(fvalues)

    # Adjust mn and mx if they are equivalent (ie, the input array
    # values are all the same number)
    if (mn == mx):
        mn -= 0.5
        mx += 0.5

    bin_width = (mx - mn) / num_bins

    # initialize the bins
    bins = [{
        'min': mn + bin_width * i,
        'max': mn + bin_width * (i + 1),
        'count': 0
    } for i in range(0, num_bins)]

    # bin the values
    for val in fvalues:
        for b in bins:
            if (val >= b['min'] and val < b['max']):
                b['count'] += 1
        # correction for when a value == the max value
        if (val == mx and b['max'] == mx):
            b['count'] += 1

    return bins
