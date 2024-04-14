from factory.fuzzy import FuzzyInteger, FuzzyText, FuzzyChoice
from fastapi import status

from fields import (
    SimpleSort,
    SortField,
    Order,
)
from .utils import get_fastapi_client


def test_field():
    sort_fields = {
        FuzzyText().fuzz(): SortField(alias=FuzzyText().fuzz())
        for _ in range(FuzzyInteger(2, 5).fuzz())
    }

    field = FuzzyChoice(sort_fields).fuzz()

    class Sort(SimpleSort):
        SORT_FIELDS = sort_fields

    fastapi_client = get_fastapi_client(Sort)
    response = fastapi_client.get(
        "/",
        params={"sort_field": field}
    )
    assert response.status_code == status.HTTP_200_OK
    content = response.json()
    assert content.pop("field") == sort_fields.get(field).alias
    assert content.pop("order") == Order.asc
    assert len(content) == 0


def test_field_not_allowed():
    sort_fields = {
        FuzzyText().fuzz(): SortField(alias=FuzzyText().fuzz())
        for _ in range(FuzzyInteger(2, 5).fuzz())
    }

    field = FuzzyText().fuzz()

    class Sort(SimpleSort):
        SORT_FIELDS = sort_fields

    fastapi_client = get_fastapi_client(Sort)
    response = fastapi_client.get(
        "/",
        params={"sort_field": field}
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_wrong_order():
    sort_fields = {FuzzyText().fuzz(): SortField(alias=FuzzyText().fuzz())}
    field = FuzzyChoice(sort_fields).fuzz()

    class Sort(SimpleSort):
        SORT_FIELDS = sort_fields

    fastapi_client = get_fastapi_client(Sort)
    response = fastapi_client.get(
        "/",
        params={"sort_field": field, "sort_order": FuzzyText().fuzz()},
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
