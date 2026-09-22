import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def client() -> TestClient:
    from app.main import create_app

    app = create_app()
    return TestClient(app)


def test_health(client: TestClient) -> None:
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_search_endpoint_returns_results(client: TestClient) -> None:
    response = client.post(
        "/api/v1/kis/search/",
        json={
            "query": "người đi xe đạp ngoài đường",
            "collection_ids": [],
            "top_k": 3,
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["query"] == "người đi xe đạp ngoài đường"
    assert body["count"] >= 0
    assert "filters" in body
    assert "parsed_keys" in body


def test_inspect_endpoint_returns_trace(client: TestClient) -> None:
    response = client.post(
        "/api/v1/kis/search/inspect/",
        json={"query": "person bicycle", "collection_ids": [], "top_k": 5},
    )
    assert response.status_code == 200
    body = response.json()
    assert "routing" in body
    assert "candidate_trace" in body


def test_planner_tool_returns_plan(client: TestClient) -> None:
    response = client.post(
        "/api/v1/kis/tools/planner",
        json={"query": "Tìm cảnh đi xe đạp", "collection_ids": ["L21"]},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["planner"].startswith("local")
    assert "objects" in body["plan"]


def test_validation_tool_returns_score(client: TestClient) -> None:
    response = client.post(
        "/api/v1/kis/tools/validation",
        json={
            "plan": {
                "objects": ["person", "bicycle"],
                "actions": ["riding"],
                "scenes": ["street"],
            },
            "results": [
                {"score": 0.7, "matched_objects": ["person", "bicycle"]},
            ],
            "threshold": 0.5,
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["accepted"] is True
    assert body["quality_score"] >= 0.5
