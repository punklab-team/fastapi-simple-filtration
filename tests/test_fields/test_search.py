from factory.fuzzy import FuzzyInteger, FuzzyText
from fastapi import status

from src import SimpleSearch
from .utils import get_fastapi_client


def test_success():

    search_fields = [
        FuzzyText().fuzz()
        for _ in range(FuzzyInteger(2, 5).fuzz())
    ]

    class Search(SimpleSearch):
        SEARCH_FIELDS = search_fields

    search_value = FuzzyText().fuzz()
    fastapi_client = get_fastapi_client(Search)
    response = fastapi_client.get("/", params={"search": search_value})
    assert response.status_code == status.HTTP_200_OK
    content = response.json()
    assert content.pop("value") == search_value
    assert content.pop("fields") == search_fields
    assert len(content) == 0
