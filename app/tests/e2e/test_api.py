from http import HTTPStatus

from fastapi.testclient import TestClient

from app.main import app


def test_health_check(client: TestClient):
    url = app.url_path_for("health")
    resp = client.get(url)
    resp_body = resp.json()
    assert resp.status_code == HTTPStatus.OK, resp_body
    assert resp_body == "ok"
