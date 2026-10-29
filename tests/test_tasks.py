import pytest

from app import create_app
from app.models import db


@pytest.fixture
def client():
    app = create_app(
        {"TESTING": True, "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:"}
    )
    with app.test_client() as client:
        yield client
    with app.app_context():
        db.drop_all()


def test_health(client):
    res = client.get("/health")
    assert res.status_code == 200
    assert res.get_json() == {"status": "ok"}


def test_create_and_list_tasks(client):
    res = client.post("/tasks", json={"title": "Learn Docker"})
    assert res.status_code == 201
    assert res.get_json()["title"] == "Learn Docker"
    assert res.get_json()["done"] is False

    res = client.get("/tasks")
    assert [t["title"] for t in res.get_json()] == ["Learn Docker"]


def test_create_task_requires_title(client):
    assert client.post("/tasks", json={}).status_code == 400
    assert client.post("/tasks", json={"title": "   "}).status_code == 400


def test_update_task(client):
    task_id = client.post("/tasks", json={"title": "Write CI"}).get_json()["id"]

    res = client.patch(f"/tasks/{task_id}", json={"done": True})
    assert res.status_code == 200
    assert res.get_json()["done"] is True


def test_delete_task(client):
    task_id = client.post("/tasks", json={"title": "Temp"}).get_json()["id"]

    assert client.delete(f"/tasks/{task_id}").status_code == 204
    assert client.get(f"/tasks/{task_id}").status_code == 404


def test_missing_task_returns_404(client):
    assert client.get("/tasks/999").status_code == 404
