import os
import shutil
import pytest
from fastapi.testclient import TestClient

from app.main import create_app
from app.database import get_db_path


@pytest.fixture
def client(monkeypatch, tmp_path):
    db_dir = tmp_path / "data"
    db_dir.mkdir()
    db_path = db_dir / "pipeline.db"

    async def override_get_db_path():
        return str(db_path)

    monkeypatch.setattr("app.database.get_db_path", override_get_db_path)

    projects_dir = tmp_path / "projects"
    projects_dir.mkdir()
    monkeypatch.setenv("PIPELINE_PROJECTS_DIR", str(projects_dir))

    app = create_app()
    with TestClient(app) as test_client:
        yield test_client

    if db_path.exists():
        db_path.unlink()


def test_health_endpoint(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "version" in data


def test_providers_endpoint(client):
    response = client.get("/api/providers")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 3
    names = {p["name"] for p in data}
    assert names == {"ollama", "claude", "gemini"}


def test_create_pipeline(client):
    response = client.post(
        "/api/pipelines",
        json={
            "project_name": "Test Project",
            "description": "A test description",
            "provider": "ollama",
            "model": "llama3.2",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["pipeline"]["project_name"] == "Test Project"
    pipeline_id = data["pipeline"]["id"]

    response = client.get(f"/api/pipelines/{pipeline_id}")
    assert response.status_code == 200
    assert response.json()["pipeline"]["id"] == pipeline_id


def test_list_pipelines(client):
    response = client.get("/api/pipelines")
    assert response.status_code == 200
    data = response.json()
    assert "pipelines" in data


def test_static_index(client):
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]


def test_static_css(client):
    response = client.get("/static/css/design-system.css")
    assert response.status_code == 200
    assert "text/css" in response.headers["content-type"]
