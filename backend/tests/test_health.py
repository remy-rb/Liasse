from fastapi.testclient import TestClient

from liasse.main import create_app
from liasse.settings import Settings


def test_health_reports_ok_when_database_is_reachable(client: TestClient) -> None:
    response = client.get("/api/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "database": "ok"}


def test_health_reports_degraded_when_database_is_unreachable(settings: Settings) -> None:
    unreachable = settings.model_copy(
        update={"database_url": "postgresql+psycopg://liasse:liasse@localhost:1/none"}
    )
    with TestClient(create_app(unreachable)) as client:
        response = client.get("/api/health")

    assert response.status_code == 200
    assert response.json() == {"status": "degraded", "database": "unreachable"}
