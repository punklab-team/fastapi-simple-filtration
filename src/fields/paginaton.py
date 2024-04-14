from fastapi import Query


class SimplePagination:

    def __init__(
        self,
        offset: int = Query(default=0),
        limit: int = Query(default=10, le=100),
    ):
        self.offset = offset
        self.limit = limit
