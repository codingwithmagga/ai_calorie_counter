import json
from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app


def test_health():
    response = TestClient(app).get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_openapi_snapshot_is_current():
    snapshot = Path(__file__).resolve().parents[1] / "openapi.json"
    assert json.loads(snapshot.read_text()) == app.openapi()
