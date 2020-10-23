from typing import Any


class QuerySet:
    def filter(self, **kwargs: Any) -> 'QuerySet':
        ...
