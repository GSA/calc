from typing import List

from .base import BaseMetric
from . import (
    dupes,
    # outliers,
    # incomplete,
    expired,
)

ALL_METRICS: List[BaseMetric] = [
    dupes.Metric(),
    # outliers.Metric(),
    # incomplete.Metric(),
    expired.Metric(),
]
