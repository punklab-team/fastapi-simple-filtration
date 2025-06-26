from factory.fuzzy import FuzzyInteger, FuzzyText, FuzzyChoice
from fastapi import status

from src import (
    SimpleInclude,
    IncludeField,
)
from .utils import get_fastapi_client


def test_field():
    include_fields = {
        FuzzyText().fuzz(): IncludeField(alias=FuzzyText().fuzz())
        for _ in range(FuzzyInteger(2, 5).fuzz())
    }

    field = FuzzyChoice(include_fields).fuzz()

    class Include(SimpleInclude):
        INCLUDE_FIELDS = include_fields

    fastapi_client = get_fastapi_client(Include.create_include_dependency())
    response = fastapi_client.get("/", params={"includeFields": field})
    assert response.status_code == status.HTTP_200_OK
    content = response.json()
    assert content.pop("fields") == [include_fields.get(field).alias]
    assert len(content) == 0


def test_field_not_allowed():
    include_fields = {
        FuzzyText().fuzz(): IncludeField(alias=FuzzyText().fuzz())
        for _ in range(FuzzyInteger(2, 5).fuzz())
    }

    field = FuzzyText().fuzz()

    class Include(SimpleInclude):
        INCLUDE_FIELDS = include_fields

    fastapi_client = get_fastapi_client(Include.create_include_dependency())
    response = fastapi_client.get("/", params={"includeFields": field})
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
