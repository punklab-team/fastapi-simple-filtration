from fields import (
    SortField,
    SimpleSort,
    FilterField,
    SimpleSearch,
    FilterOperator,
    SimpleFiltration,
    SimplePagination,
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
            alias="players.mainTeam",
            field_type=str,
            operators=[FilterOperator.eq, FilterOperator.contains],
        ),
    }
