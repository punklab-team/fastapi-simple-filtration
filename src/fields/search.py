from typing import List
from fastapi import HTTPException, Query


class SimpleSearch:
    SEARCH_FIELDS: List[str] = []

    def __init__(self, search: str = Query(default=None)) -> None:
        if search:
            if not self.SEARCH_FIELDS:
                raise HTTPException("Search is not allowed.")
            self.value = search
            self.fields = self.SEARCH_FIELDS
        else:
            self.value = None
            self.fields = None
