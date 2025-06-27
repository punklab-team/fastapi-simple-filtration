import json
from typing import List

import pytest
from factory.fuzzy import FuzzyInteger, FuzzyText, FuzzyChoice
from fastapi import status

from src.fastapi_filter import (
    SimpleFiltration,
    FilterOperator,
    FilterField,
)
from .utils import get_fastapi_client


def __get_value_by_type(_type):
    if _type == str:
        return FuzzyText().fuzz()
    if _type == int:
        return FuzzyInteger(1, 100).fuzz()
    if _type == float:
        return FuzzyInteger(1, 100).fuzz()
    if _type == List[str]:
        return [FuzzyText().fuzz() for _ in range(3)]


def test_success__one_filter():
    fields = {
        FuzzyText().fuzz(): FilterField(field_type=str)
        for _ in range(FuzzyInteger(3, 5).fuzz())
    }

    class Filters(SimpleFiltration):
        FILTER_FIELDS = fields

    field = FuzzyChoice(fields).fuzz()

    request_filters = [field, FilterOperator.eq, __get_value_by_type(str)]
    filters = [
        {
            "field_name": request_filters[0],
            "operator": request_filters[1],
            "value": request_filters[2],
        }
    ]

    fastapi_client = get_fastapi_client(Filters)
    response = fastapi_client.get(
        "/",
        params={"filters": json.dumps(request_filters)},
    )
    assert response.status_code == status.HTTP_200_OK, response.json()
    content = response.json()
    assert filters[0] == content.pop("filters")
    assert len(content) == 0


@pytest.mark.parametrize(
    "_type,operators",
    (
        (str, ["eq", "ne", "has"]),
        (int, ["eq", "ne", "gt", "lt", "gte", "lte"]),
        (float, ["eq", "ne", "gt", "lt", "gte", "lte"]),
        (List[str], ["eq", "ne", "contains_any", "contains_all"]),
    ),
)
def test_success__operators(_type, operators):
    fields = {
        FuzzyText().fuzz(): FilterField(field_type=_type)
        for _ in range(FuzzyInteger(3, 5).fuzz())
    }

    class Filters(SimpleFiltration):
        FILTER_FIELDS = fields

    field = FuzzyChoice(fields).fuzz()

    request_filters = []
    filters = []
    for operator in operators:
        value = __get_value_by_type(_type)
        request_filters.append([field, operator, value])
        request_filters.append("and")
        filters.append(
            {
                "field_name": field,
                "operator": operator,
                "value": value,
            },
        )
        filters.append("and")
    request_filters.pop()
    filters.pop()

    fastapi_client = get_fastapi_client(Filters)
    response = fastapi_client.get(
        "/",
        params={"filters": json.dumps(request_filters)},
    )
    assert response.status_code == status.HTTP_200_OK, response.json()
    content = response.json()
    assert filters == content.pop("filters")
    assert len(content) == 0


def test_fail__wrong_field_name():
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


def test_fail__operator_not_allowed__specified():
    operators = list(FilterOperator)
    operators_allowed = operators[::2]
    operators_disallowed = operators[1::2]

    fields = {
        FuzzyText().fuzz(): FilterField(
            field_type=str,
            operators=operators_allowed,
        )
        for _ in range(FuzzyInteger(3, 5).fuzz())
    }

    class Filters(SimpleFiltration):
        FILTER_FIELDS = fields

    field_name = FuzzyChoice(fields).fuzz()
    wrong_operator = FuzzyChoice(operators_disallowed).fuzz()
    request_filters = [field_name, wrong_operator, FuzzyText().fuzz()]

    fastapi_client = get_fastapi_client(Filters)
    response = fastapi_client.get(
        "/",
        params={"filters": json.dumps(request_filters)},
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.parametrize(
    "_type,operators_allowed",
    (
        (str, ["eq", "ne", "has"]),
        (int, ["eq", "ne", "gt", "lt", "gte", "lte"]),
        (float, ["eq", "ne", "gt", "lt", "gte", "lte"]),
        (List[str], ["eq", "ne", "contains_any", "contains_all"]),
    ),
)
def test_fail__operator_not_allowed__not_specified(_type, operators_allowed):
    operators = list(FilterOperator)
    operators_disallowed = list(set(operators) - set(operators_allowed))

    field_name = FuzzyText().fuzz()
    fields = [
        {
            field_name: FilterField(
                field_type=_type,
                operators=operators_allowed,
            )
        }
    ]

    class Filters(SimpleFiltration):
        FILTER_FIELDS = fields

    wrong_operator = FuzzyChoice(operators_disallowed).fuzz()
    request_filters = [field_name, wrong_operator, __get_value_by_type(_type)]

    fastapi_client = get_fastapi_client(Filters)
    response = fastapi_client.get(
        "/",
        params={"filters": json.dumps(request_filters)},
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_fail__wrong_convert_type():
    fields = {
        FuzzyText().fuzz(): FilterField(
            field_type=int,
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


def test_fail__logical_operator_not_found():

    class Filters(SimpleFiltration):
        FILTER_FIELDS = {}

    fastapi_client = get_fastapi_client(Filters)
    request_filters = [[FuzzyText().fuzz()] * 3] * 3
    response = fastapi_client.get(
        "/",
        params={"filters": json.dumps(request_filters)},
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert (
        response.json()["detail"]
        == "Логический оператор ['and', 'or'] не найден на позиции 2."
    )


def test_fail__wrong_filter_format():

    class Filters(SimpleFiltration):
        FILTER_FIELDS = {}

    fastapi_client = get_fastapi_client(Filters)
    response = fastapi_client.get(
        "/",
        params={"filters": FuzzyText().fuzz()},
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_sucess__empty_filter():
    fields = {
        FuzzyText().fuzz(): FilterField(
            field_type=str,
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


def test_success__empty_alias():
    fields = {
        FuzzyText().fuzz(): FilterField(
            field_type=str,
            operators=[FilterOperator.eq, FilterOperator.has],
        )
    }

    class Filters(SimpleFiltration):
        FILTER_FIELDS = fields

    field_name = FuzzyChoice(fields).fuzz()
    request_filter = [
        field_name,
        FilterOperator.eq,
        FuzzyText().fuzz(),
    ]

    fastapi_client = get_fastapi_client(Filters)
    response = fastapi_client.get(
        "/",
        params={"filters": json.dumps(request_filter)},
    )
    assert response.status_code == status.HTTP_200_OK
    content = response.json()
    assert len(content["filters"]) == 3
    response_filter = content["filters"]
    assert response_filter["field_name"] == request_filter[0]
    assert response_filter["operator"] == request_filter[1]
    assert response_filter["value"] == request_filter[2]


def test_success__nested_filtering():
    fields = {
        FuzzyText().fuzz(): FilterField(field_type=str)
        for _ in range(FuzzyInteger(3, 5).fuzz())
    }

    class Filters(SimpleFiltration):
        FILTER_FIELDS = fields

    def gen_(filters: list, n):
        """Генерация вложенной фильтрации с заданной глубиной"""
        for filter_ in filters:
            if FuzzyChoice([True, False]).fuzz() or n == 2:
                filter_ += [
                    FuzzyChoice(fields).fuzz(),
                    FilterOperator.eq,
                    FuzzyText().fuzz(),
                ]
            else:
                filter_.append(
                    list([] for _ in range(FuzzyInteger(2, 3).fuzz())),
                )
                gen_(filter_[-1], n + 1)
        for i in range(1, len(filters) + 1, 2):
            filters.insert(i, FuzzyChoice(["and", "or"]).fuzz())
        return filters

    filters = gen_([[], [], []], 0)

    def parse_(filters: list):
        """Парсинг фильтрации"""
        result = []
        if isinstance(filters[0], str):
            result = {
                "field_name": filters[0],
                "operator": filters[1],
                "value": filters[2],
            }
        elif isinstance(filters[0], list):
            for filter_ in filters:
                if isinstance(filter_, list):
                    result.append(parse_(filter_))
                elif isinstance(filter_, str):
                    result.append(filter_)
        return result

    parsed_filters = parse_(filters)

    fastapi_client = get_fastapi_client(Filters)
    response = fastapi_client.get("/", params={"filters": json.dumps(filters)})
    assert response.status_code == status.HTTP_200_OK, response.json()
    content = response.json()
    assert parsed_filters == content.pop("filters")
