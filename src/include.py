from typing import Set
from enum import Enum
from fastapi import Query, status, HTTPException
from pydantic import BaseModel

from .base import Base


class IncludeField(BaseModel):
    alias: str


class SimpleInclude(Base):
    INCLUDE_FIELDS = {}

    @classmethod
    def _get_include_fields_enum(cls) -> Enum:
        """Динамически создает Enum из ключей INCLUDE_FIELDS"""
        return Enum(
            "IncludeFields",
            {field: field for field in cls.INCLUDE_FIELDS.keys()},
        )

    @classmethod
    def as_dependency(cls):
        """Фабрика для создания зависимости"""
        IncludeFieldsEnum = cls._get_include_fields_enum()

        async def wrapper(
            include_fields: Set[IncludeFieldsEnum] = Query(     # type: ignore
                default=None,
                alias="includeFields",
                description=(
                    "Поля для включения в ответ. "
                    "Если не указаны - возвращаются все поля"
                ),
            ),
        ) -> "SimpleInclude":

            return cls(fields={field.name for field in include_fields})

        return wrapper

    def __init__(self, fields: Set):
        if fields:
            extra_fields = fields - set(self.INCLUDE_FIELDS)
            if extra_fields:
                raise HTTPException(
                    status.HTTP_422_UNPROCESSABLE_ENTITY,
                    f"Wrong field names {extra_fields} for include fields.",
                )
            self.fields = [
                self.INCLUDE_FIELDS[field].alias
                for field in fields
            ]
        else:
            self.fields = None
