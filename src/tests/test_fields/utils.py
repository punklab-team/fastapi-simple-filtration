from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient


def get_fastapi_client(dependency) -> TestClient:
    app = FastAPI()

    @app.get("/")
    def _(_=Depends(dependency)):
        return _
    return TestClient(app)
