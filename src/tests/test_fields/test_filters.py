import json
from factory.fuzzy import FuzzyInteger, FuzzyText, FuzzyChoice
from fastapi import status

from fields import (
    SimpleFiltration,
    FilterOperator,
    FilterField,
)
from .utils import get_fastapi_client


def test_success():
    fields = {
        FuzzyText().fuzz(): FilterField(
            alias=FuzzyText().fuzz(),
            field_type=str,
            operators=[FilterOperator.eq, FilterOperator.has],
        )
        for _ in range(FuzzyInteger(3, 5).fuzz())
    }

    class Filters(SimpleFiltration):
        FILTER_FIELDS = fields

    field_1 = FuzzyChoice(fields).fuzz()
    field_2 = FuzzyChoice(fields).fuzz()

    request_filters = [
        (field_1, FilterOperator.eq, FuzzyText().fuzz()),
        (field_1, FilterOperator.has, FuzzyText().fuzz()),
        (field_2, FilterOperator.has, FuzzyText().fuzz()),
    ]

    filters = []
    for field, operator, value in request_filters:
        filters.append(
            {
                "field_name": fields[field].alias,
                "operator": operator,
                "value": value,
            },
        )

    fastapi_client = get_fastapi_client(Filters)
    response = fastapi_client.get(
        "/",
        params={"filters": json.dumps(request_filters)},
    )
    assert response.status_code == status.HTTP_200_OK, response.json()
    content = response.json()
    assert filters == content.pop("filters")
    assert len(content) == 0


def test_wrong_field_name():
    fields = {
        FuzzyText().fuzz(): FilterField(
            alias=FuzzyText().fuzz(),
            field_type=str,
            operators=[FilterOperator.eq, FilterOperator.has],
        )
        for _ in range(FuzzyInteger(3, 5).fuzz())
    }

    class Filters(SimpleFiltration):
        FILTER_FIELDS = fields

    request_filters = [
        (FuzzyText().fuzz(), FilterOperator.eq, FuzzyText().fuzz()),
    ]

    fastapi_client = get_fastapi_client(Filters)
    response = fastapi_client.get(
        "/",
        params={"filters": json.dumps(request_filters)},
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_operator_not_allowed():
    operators = list(FilterOperator)
    operators_allowed = operators[::2]
    operators_disallowed = operators[1::2]

    fields = {
        FuzzyText().fuzz(): FilterField(
            alias=FuzzyText().fuzz(),
            field_type=str,
            operators=operators_allowed,
        )
        for _ in range(FuzzyInteger(3, 5).fuzz())
    }

    class Filters(SimpleFiltration):
        FILTER_FIELDS = fields

    field_name = FuzzyChoice(fields).fuzz()
    wrong_operator = FuzzyChoice(operators_disallowed).fuzz()
    request_filters = [[field_name, wrong_operator, FuzzyText().fuzz()]]

    fastapi_client = get_fastapi_client(Filters)
    response = fastapi_client.get(
        "/",
        params={"filters": json.dumps(request_filters)},
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_wrong_convert_type():
    fields = {
        FuzzyText().fuzz(): FilterField(
            alias=FuzzyText().fuzz(),
            field_type=int,
            operators=[FilterOperator.eq, FilterOperator.has],
        )
    }

    class Filters(SimpleFiltration):
        FILTER_FIELDS = fields

    field_name = FuzzyChoice(fields).fuzz()
    request_filters = [
        (field_name, FilterOperator.eq, FuzzyText().fuzz()),
    ]

    fastapi_client = get_fastapi_client(Filters)
    response = fastapi_client.get(
        "/",
        params={"filters": json.dumps(request_filters)},
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_filter_items_isnt_three():

    class Filters(SimpleFiltration):
        FILTER_FIELDS = {}

    fastapi_client = get_fastapi_client(Filters)
    for count_filters in [2, 4]:
        four_filters = [[FuzzyText().fuzz()] * count_filters]
        response = fastapi_client.get(
            "/",
            params={"filters": json.dumps(four_filters)},
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert (
            response.json()["detail"]
            == "Filtration is list of lists of 3 elements."
        )


def test_wrong_filter_format():

    class Filters(SimpleFiltration):
        FILTER_FIELDS = {}

    fastapi_client = get_fastapi_client(Filters)
    response = fastapi_client.get(
        "/",
        params={"filters": FuzzyText().fuzz()},
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_empty_filter():
    fields = {
        FuzzyText().fuzz(): FilterField(
            alias=FuzzyText().fuzz(),
            field_type=str,
            operators=[FilterOperator.eq, FilterOperator.has],
        )
    }

    class Filters(SimpleFiltration):
        FILTER_FIELDS = fields

    fastapi_client = get_fastapi_client(Filters)
    response = fastapi_client.get(
        "/",
        params={"filters": "[]"},
    )
    assert response.status_code == status.HTTP_200_OK
    content = response.json()
    assert [] == content.pop("filters")


def test_empty_alias():
    fields = {
        FuzzyText().fuzz(): FilterField(
            field_type=str,
            operators=[FilterOperator.eq, FilterOperator.has],
        )
    }

    class Filters(SimpleFiltration):
        FILTER_FIELDS = fields

    field_name = FuzzyChoice(fields).fuzz()
    request_filters = [
        (field_name, FilterOperator.eq, FuzzyText().fuzz()),
    ]

    fastapi_client = get_fastapi_client(Filters)
    response = fastapi_client.get(
        "/",
        params={"filters": json.dumps(request_filters)},
    )
    assert response.status_code == status.HTTP_200_OK
    content = response.json()
    assert len(content["filters"]) == 1
    response_filter = content["filters"][0]
    request_filter = request_filters[0]
    assert response_filter["field_name"] == request_filter[0]
    assert response_filter["operator"] == request_filter[1]
    assert response_filter["value"] == request_filter[2]
