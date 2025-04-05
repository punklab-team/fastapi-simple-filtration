import json
from enum import Enum
from typing import Any, AnyStr, Dict, List, Union, get_args, get_origin

from fastapi import HTTPException, Query, status
from pydantic import BaseModel


WRONG_FORMAT_MESSAGE = "Неверный формат фильтров."
WRONG_FILER_SIZE_MESSAGE = "Фильтрация — это список списков из 3 элементов."
FIELD_IS_NOT_ALLOWED_MESSAGE \
    = "Фильтрация по полю '{field_name}' не разрешена."
OPERATOR_IS_NOT_ALLOWED_MESSAGE = "Оператор '{operator}' не разрешен."
WRONG_VALUE_FORMAT_MESSAGE = "Значение '{value}' имеет неверный формат."
WRONG_ARRAY_FORMAT_MESSAGE = "Значение должно быть в формате массива."
LOGICAL_OPERATOR_NOT_FOUND \
    = "Логический оператор {operators} не найден на позиции {position}."


class FilterOperator(str, Enum):
    """
    Enum для операторов фильтрации.

    :param str eq: Оператор "равно".
    :param str ne: Оператор "не равно".
    :param str ge: Оператор "больше или равно".
    :param str le: Оператор "меньше или равно".
    :param str gte: Оператор "больше".
    :param str lte: Оператор "меньше".
    :param str has: Проверка на существование значения.
    :param str contains_any: Проверка на наличие хотя бы
    одного значения в списке.
    :param str contains_all: Проверка на наличие всех значений в списке.
    """

    eq = "eq"
    ne = "ne"
    ge = "ge"
    le = "le"
    gte = "gte"
    lte = "lte"
    has = "has"
    contains_any = "contains_any"
    contains_all = "contains_all"

    def __str__(self):
        """
        Возвращает строковое представление оператора.

        :return: str: Строковое представление оператора.
        """
        return f"{self.value}"

    def __repr__(self):
        """
        Возвращает представление оператора.

        :return: repr: Представление оператора.
        """
        return repr(self.value)


_TYPE_OPERATORS_MAP = {
    str: ["eq", "ne", "has"],
    int: ["eq", "ne", "ge", "le", "gte", "lte"],
    float: ["eq", "ne", "ge", "le", "gte", "lte"],
    list: ["eq", "ne", "contains_any", "contains_all"],
}


class FilterResponse(BaseModel):
    """
    Модель Pydantic для ответа фильтрации.

    :param str field_name: Имя поля, по которому проводится фильтрация.
    :param FilterOperator operator: Оператор фильтрации,
    который будет использоваться.
    :param Any value: Значение для фильтрации.
    """
    field_name: AnyStr
    operator: FilterOperator
    value: Any


class FilterField:
    """
    Представляет поле с логикой фильтрации.

    :param type field_type: Тип данных поля.
    :param List[FilterOperator] operators: Список разрешённых операторов
    фильтрации для этого поля.
    :param str alias: Необязательный псевдоним для поля.
    """
    NESTING_SIMBOL = "__"
    SWAP_NESTING_SIMBOL = "->"

    def __init__(
        self,
        field_type,
        operators: Union[List[FilterOperator], None] = None,
        alias=None,
    ) -> None:
        """
        Инициализирует объект FilterField.

        :param field_type: Тип данных поля.
        :param operators: Список разрешённых операторов фильтрации.
        :param alias: Необязательный псевдоним для поля.
        """
        self.alias = alias
        self.field_type = field_type
        self.operators = operators

    def __get_operator(self, operator):
        """
        Проверяет и возвращает оператор.

        :param str operator: Оператор фильтрации.
        :return: Подтверждённый оператор.
        :raises HTTPException: Если оператор не разрешён.
        """
        _type = get_origin(self.field_type) or self.field_type
        if self.operators:
            operators = self.operators
        else:
            operators = _TYPE_OPERATORS_MAP.get(_type, [])
        if operator in operators:
            return operator

        raise HTTPException(
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            OPERATOR_IS_NOT_ALLOWED_MESSAGE.format(operator=operator),
        )

    def __convert_value(self, value):
        """
        Преобразует переданное значение в тип поля.

        :param value: Значение для преобразования.
        :return: Преобразованное значение.
        :raises HTTPException: Если значение не может быть преобразовано.
        """
        try:
            _type = self.field_type
            if get_origin(self.field_type) is list:
                _type = get_args(self.field_type)[0]
            return _type(value)
        except Exception:
            raise HTTPException(
                status.HTTP_422_UNPROCESSABLE_ENTITY,
                WRONG_VALUE_FORMAT_MESSAGE.format(value=value),
            )

    def __get_value(self, value):
        """
        Получает значение после применения необходимых преобразований.

        :param value: Значение для преобразования.
        :return: Преобразованное значение.
        :raises HTTPException: Если формат значения некорректен.
        """
        if isinstance(value, list):
            return list(map(self.__convert_value, value))
        return self.__convert_value(value)

    def __get_field_name(self, name):
        """
        Получает имя поля, заменяя символы вложенности, если это необходимо.

        :param str name: Имя поля.
        :return: Имя поля или его псевдоним.
        """
        return (
            self.alias
            or name.replace(
                self.NESTING_SIMBOL,
                self.SWAP_NESTING_SIMBOL,
            )
        )

    def get_filter(self, name, operator, value):
        """
        Получает ответ фильтрации для поля.

        :param str name: Имя поля.
        :param str operator: Оператор фильтрации.
        :param value: Значение для фильтрации.
        :return: dict: Словарь, представляющий ответ фильтра.
        """
        return FilterResponse(
            field_name=self.__get_field_name(name),
            operator=self.__get_operator(operator),
            value=self.__get_value(value),
        ).dict()


class SimpleFiltration:
    """
    Обрабатывает фильтрацию параметров запроса.

    :param str filter_: Строка фильтров, представляющая условия,
    по умолчанию Query(default="[]", alias="filters").
    :raises HTTPException: Если формат фильтра некорректен.
    """
    FILTER_FIELDS: Dict[str, FilterField] = {}
    LOGICAL_OPERATORS = {"and", "or"}

    def __init__(self, filter_: str = Query(default="[]", alias="filters")):
        """
        Инициализирует систему фильтрации.

        :param filter_: Строка в формате JSON, представляющая фильтры
        (по умолчанию "[]").
        :raises HTTPException: Если формат фильтра некорректен.
        """
        try:
            filter_ = json.loads(filter_)
        except json.decoder.JSONDecodeError:
            raise HTTPException(
                status.HTTP_422_UNPROCESSABLE_ENTITY,
                WRONG_FORMAT_MESSAGE,
            )
        self.filters = filter_ and self.parse_filter(filter_)

    def parse_filter(self, filter_: Union[List, str]) -> Union[dict, List]:
        """
        Парсит строку фильтра в используемый формат фильтра.

        :param filter_: Фильтр для парсинга.
        :return: Парсированный фильтр в виде словаря или списка.
        :raises HTTPException: Если формат фильтра некорректен.
        """

        if self.__is_simple_filter(filter_):
            return self.create_filter(filter_)

        result = []
        if self.__is_group_of_filters(filter_):
            for operator_index in range(1, len(filter_), 2):
                logical_operator = (
                    filter_[operator_index]
                    if (
                        isinstance(filter_[operator_index], str)
                        and filter_[operator_index] in self.LOGICAL_OPERATORS
                    )
                    else None
                )
                if not logical_operator:
                    raise HTTPException(
                        status.HTTP_422_UNPROCESSABLE_ENTITY,
                        LOGICAL_OPERATOR_NOT_FOUND.format(
                            operators=sorted(self.LOGICAL_OPERATORS),
                            position=operator_index + 1,
                        )
                    )
                result.append(self.parse_filter(filter_[operator_index - 1]))
                result.append(filter_[operator_index])
            result.append(self.parse_filter(filter_[-1]))
            return result
        raise HTTPException(
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            WRONG_FORMAT_MESSAGE,
        )

    def create_filter(self, filter_: List[str]) -> dict:
        """
        Создаёт фильтр из списка компонентов фильтра.

        :param filter_: Список, представляющий условие фильтра
        [поле, оператор, значение].
        :return: Словарь, представляющий фильтр.
        :raises HTTPException: Если поле не разрешено.
        """
        field, operator, value = filter_
        if field not in self.FILTER_FIELDS:
            raise HTTPException(
                status.HTTP_422_UNPROCESSABLE_ENTITY,
                FIELD_IS_NOT_ALLOWED_MESSAGE.format(field_name=field),
            )
        return self.FILTER_FIELDS[field].get_filter(field, operator, value)

    def __is_simple_filter(self, filter_: List) -> bool:
        """
        Проверяет, является ли фильтр простым фильтром.

        :param filter_: Фильтр для проверки.
        :return: True, если это простой фильтр, иначе False.
        """
        return (
            isinstance(filter_, list)
            and len(filter_) == 3
            and isinstance(filter_[0], str)
        )

    def __is_group_of_filters(self, filter_: List) -> bool:
        """
        Проверяет, является ли фильтр простым фильтром.

        :param filter_: Фильтр для проверки.
        :return: True, если это простой фильтр, иначе False.
        """
        return (
            isinstance(filter_, list)
            and len(filter_) % 2 == 1
        )
