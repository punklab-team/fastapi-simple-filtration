import uvicorn
from fastapi import Depends, FastAPI
from .filters import (
    RootSorting,
    RootSearching,
    RootFiltration,
    RootPagination,
    RootIncluding,
)

app = FastAPI()


@app.get("/root")
async def root(
    sorting=Depends(RootSorting.create_sort_dependency()),
    searching=Depends(RootSearching.create_search_dependency()),
    filters=Depends(RootFiltration.create_filter_dependency()),
    pagination=Depends(RootPagination),
    include=Depends(RootIncluding.create_include_dependency()),
):
    return {
        "sorting": sorting,
        "searching": searching,
        "filters": filters,
        "pagination": pagination,
        "include": include,
    }

if __name__ == "__main__":
    uvicorn.run(app)
