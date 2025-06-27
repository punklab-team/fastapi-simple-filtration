class Base:
    """
    Базовый класс для всех классов, которые могут
    быть использованы как зависимости.
    """

    @classmethod
    def as_dependency(cls):
        """Фабрика для создания зависимости FastAPI"""
        raise NotImplementedError(
            "Метод as_dependency должен быть реализован в подклассе",
        )
