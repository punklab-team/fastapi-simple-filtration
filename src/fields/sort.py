from enum import Enum

from fastapi import HTTPException, Query, status


class Order(str, Enum):
    asc = "asc"
    desc = "desc"

    def __str__(self):
        return f"{self.value}"

    def __repr__(self):
        return repr(self.value)


class SortField:
    def __init__(self, alias: str) -> None:
        self.alias = alias


class SimpleSort:
    SORT_FIELDS = {}

    def __init__(
        self,
        sort_field: str = Query(default=None),
        sort_order: Order = Query(default=Order.asc),
    ) -> None:
        if sort_field:
            sort_class = self.SORT_FIELDS.get(sort_field)
            if not sort_class:
                raise HTTPException(
                    status.HTTP_422_UNPROCESSABLE_ENTITY,
                    f"Sort by field '{sort_field}' is not allowed.",
                )
            self.field = sort_class.alias
            self.order = sort_order
        else:
            self.field = None
            self.order = None
