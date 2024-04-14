from factory.fuzzy import FuzzyInteger
from fastapi import Query, status

from fields import SimplePagination
from .utils import get_fastapi_client


def test_call():
    class Pagination(SimplePagination):
        pass

    offset, limit = FuzzyInteger(100).fuzz(), FuzzyInteger(100).fuzz()
    pagination = Pagination(offset=offset, limit=limit)
    assert pagination.offset == offset
    assert pagination.limit == limit


def test_limit_exceeded():
    default_limit = FuzzyInteger(10, 100).fuzz()
    max_limit = FuzzyInteger(100, 200).fuzz()

    class Pagination(SimplePagination):

        def __init__(
            self,
            offset: int = Query(default=0),
            limit: int = Query(default=default_limit, le=max_limit),
        ):
            super().__init__(offset, limit)

    fastapi_client = get_fastapi_client(Pagination)
    response = fastapi_client.get("/", params={"limit": max_limit})
    assert response.status_code == status.HTTP_200_OK
    response = fastapi_client.get("/", params={"limit": max_limit + 1})
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_default_offset_and_limit():
    default_offset = FuzzyInteger(0, 100).fuzz()
    default_limit = FuzzyInteger(0, 100).fuzz()

    class Pagination(SimplePagination):

        def __init__(
            self,
            offset: int = Query(default=default_offset),
            limit: int = Query(default=default_limit, le=0),
        ):
            super().__init__(offset, limit)

    fastapi_client = get_fastapi_client(Pagination)
    response = fastapi_client.get("/")
    assert response.status_code == status.HTTP_200_OK
    content = response.json()
    assert content.pop("offset") == default_offset
    assert content.pop("limit") == default_limit
    assert len(content) == 0
