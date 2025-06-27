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
    sorting=Depends(RootSorting.as_dependency()),
    searching=Depends(RootSearching.as_dependency()),
    filters=Depends(RootFiltration.as_dependency()),
    pagination=Depends(RootPagination.as_dependency()),
    include=Depends(RootIncluding.as_dependency()),
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
