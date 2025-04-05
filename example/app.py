import uvicorn
from fastapi import Depends, FastAPI
from .filters import (
    RootSorting,
    RootSearching,
    RootFiltration,
    RootPagination,
)


app = FastAPI()


@app.get("/root")
async def root(
    sorting=Depends(RootSorting),
    searching=Depends(RootSearching),
    filters=Depends(RootFiltration),
    pagination=Depends(RootPagination),
):
    return {
        "sorting": sorting,
        "searching": searching,
        "filters": filters,
        "pagination": pagination,
    }

if __name__ == "__main__":
    uvicorn.run(app)
