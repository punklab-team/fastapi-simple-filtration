from typing import List, Optional
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

    @classmethod
    def create_search_dependency(cls):
        """Фабрика для создания зависимости"""

        async def search_dependency(
            search: Optional[str] = Query(
                default=None,
                description=f"Поисковой запрос (ищет по полю(полям): "
                f"{', '.join(cls.SEARCH_FIELDS)})",
            ),
        ) -> "SimpleSearch":

            return cls(search=search)

        return search_dependency

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
