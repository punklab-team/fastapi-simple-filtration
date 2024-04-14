import json
from enum import Enum
from typing import Any, AnyStr, Dict, List

from fastapi import HTTPException, Query, status
from pydantic import BaseModel


WRONG_FORMAT_MESSAGE = "Wrong filters format."
WRONG_FILER_SIZE_MESSAGE = "Filtration is list of lists of 3 elements."
FIELD_IS_NOT_ALLOWED_MESSAGE = "Filter by field '{field_name}' is not allowed."
OPERATOR_IS_NOT_ALLOWED_MESSAGE = "Operator '{operator}' is not allowed."
WRONG_VALUE_FORMAT_MESSAGE = "Value '{value}' has wrong format."
WRONG_ARRAY_FORMAT_MESSAGE = "Value shoud be an array format."


class FilterOperator(str, Enum):
    eq = "eq"
    ne = "ne"
    ge = "ge"
    le = "le"
    gte = "gte"
    lte = "lte"
    has = "has"
    contains = "contains"

    def __str__(self):
        return f"{self.value}"

    def __repr__(self):
        return repr(self.value)


class FilterResponse(BaseModel):
    field_name: AnyStr
    operator: FilterOperator
    value: Any


class FilterField:
    def __init__(
        self,
        field_type,
        operators: List[FilterOperator],
        alias=None,
    ) -> None:
        self.alias = alias
        self.field_type = field_type
        self.operators = operators

    def __get_operator(self, operator):
        if operator not in self.operators:
            raise HTTPException(
                status.HTTP_422_UNPROCESSABLE_ENTITY,
                OPERATOR_IS_NOT_ALLOWED_MESSAGE.format(operator=operator),
            )
        return operator

    def __convert_value(self, value):
        try:
            return self.field_type(value)
        except Exception:
            raise HTTPException(
                status.HTTP_422_UNPROCESSABLE_ENTITY,
                WRONG_VALUE_FORMAT_MESSAGE.format(value=value),
            )

    def __get_value(self, value, operator):
        if operator == FilterOperator.contains:
            if not isinstance(value, list):
                raise HTTPException(
                    status.HTTP_422_UNPROCESSABLE_ENTITY,
                    WRONG_ARRAY_FORMAT_MESSAGE,
                )
            return list(map(self.__convert_value, value))
        return self.__convert_value(value)

    def get_filter(self, name, operator, value):
        return FilterResponse(
            field_name=self.alias or name,
            operator=self.__get_operator(operator),
            value=self.__get_value(value, operator),
        ).dict()


class SimpleFiltration:
    FILTER_FIELDS: Dict[str, FilterField] = {}

    def __init__(
        self,
        filters: str = Query(default="[]", alias="filters"),
    ):
        try:
            filters = json.loads(filters)
        except json.decoder.JSONDecodeError:
            raise HTTPException(
                status.HTTP_422_UNPROCESSABLE_ENTITY,
                WRONG_FORMAT_MESSAGE,
            )
        self.filters = []
        for filter_ in filters:
            self.__validate_filter(filter_)
            filter_class = self.FILTER_FIELDS.get(filter_[0])
            if not filter_class:
                raise HTTPException(
                    status.HTTP_422_UNPROCESSABLE_ENTITY,
                    FIELD_IS_NOT_ALLOWED_MESSAGE.format(field_name=filter_[0])
                )
            self.filters.append(filter_class.get_filter(*filter_))

    def __validate_filter(self, filter_):
        if len(filter_) != 3:
            raise HTTPException(
                status.HTTP_422_UNPROCESSABLE_ENTITY,
                WRONG_FILER_SIZE_MESSAGE,
            )
