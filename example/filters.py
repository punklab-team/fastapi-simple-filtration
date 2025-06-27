from src.fastapi_filter import (
    SortField,
    SimpleSort,
    FilterField,
    SimpleSearch,
    FilterOperator,
    SimpleFiltration,
    SimplePagination,
    SimpleInclude,
    IncludeField,
)


class RootPagination(SimplePagination):
    pass


class RootSorting(SimpleSort):
    SORT_FIELDS = {
        "players__mainTeam": SortField(alias="players.mainTeam"),
    }


class RootSearching(SimpleSearch):
    SEARCH_FIELDS = ["players.mainTeam"]


class RootFiltration(SimpleFiltration):
    FILTER_FIELDS = {
        "players__mainTeam": FilterField(
            field_type=str,
            operators=[FilterOperator.eq, FilterOperator.contains_all],
        ),
    }


class RootIncluding(SimpleInclude):
    INCLUDE_FIELDS = {
        "id": IncludeField(alias="_id"),
        "name": IncludeField(alias="name"),
        "phone": IncludeField(alias="phone"),
        "teams": IncludeField(alias="teams"),
        "teams__id": IncludeField(alias="teams.id"),
        "teams__name": IncludeField(alias="teams.name"),
        "teams__imageUrl": IncludeField(alias="teams.img"),
        "telegramAccess": IncludeField(alias="telegram_access"),
        "telegramAccess__status": IncludeField(
            alias="telegram_access.status",
        ),
        "telegramAccess__remainingAttempts": IncludeField(
            alias="telegram_access.remainingAttempts",
        ),
    }
