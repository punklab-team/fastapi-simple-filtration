from fastapi import Query

from .base import Base


class SimplePagination(Base):

    """
    Класс для управления пагинацией.

    Этот класс используется для получения данных о пагинации,
    таких как смещение (offset)
    и ограничение (limit) количества элементов на странице.

    :param int offset: Смещение (начальная позиция). По умолчанию 0.
    :param int limit: Максимальное количество элементов на странице.
    По умолчанию 10, максимальное значение — 100.
    """

    OFFSET = 0
    LIMIT_DEFAULT = 10
    LIMIT_MAX = 100

    @classmethod
    def as_dependency(cls):
        """Фабрика для создания зависимости"""

        async def wrapper(
            offset: int = Query(
                default=cls.OFFSET,
                description="Смещение от начала списка",
            ),
            limit: int = Query(
                default=cls.LIMIT_DEFAULT,
                le=cls.LIMIT_MAX,
                description="Количество возвращаемых элементов",
            ),
        ) -> "SimplePagination":

            return cls(offset=offset, limit=limit)

        return wrapper

    def __init__(
        self,
        offset,
        limit,
    ):
        """
        Инициализирует параметры пагинации.

        :param int offset: Смещение для пагинации (по умолчанию 0).
        :param int limit: Максимальное количество элементов на странице
        (по умолчанию 10, не более 100).
        """
        self.offset = offset
        self.limit = limit
