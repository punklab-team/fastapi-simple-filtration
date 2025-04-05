from typing import List
from fastapi import HTTPException, Query


class SimpleSearch:
    """
    Класс для реализации функционала поиска.

    Этот класс используется для получения значения поискового
    запроса и определения полей, по которым можно выполнять поиск.
    Если поисковый запрос не пустой, то класс проверяет,
    есть ли разрешённые поля для поиска. Если поля не заданы,
    будет вызвано исключение.

    :param str search: Строка для поискового запроса. По умолчанию None.
    """

    SEARCH_FIELDS: List[str] = []

    def __init__(self, search: str = Query(default=None)) -> None:
        """
        Инициализирует параметры поиска.

        :param str search: Строка для поискового запроса.
        Если передана, проверяется, разрешены ли поля для поиска.
        :raises HTTPException: Если поля для поиска не заданы в
        `SEARCH_FIELDS`, выбрасывается исключение.
        """
        if search:
            if not self.SEARCH_FIELDS:
                raise HTTPException(
                    status_code=400,
                    detail="Search is not allowed.",
                )
            self.value = search
            self.fields = self.SEARCH_FIELDS
        else:
            self.value = None
            self.fields = None
