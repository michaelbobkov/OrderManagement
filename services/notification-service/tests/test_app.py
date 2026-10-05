from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "UP"


def test_event_accepted_and_counted():
    r = client.post("/events", json={"type": "order.created", "order_id": "1",
                                     "customer": "alice", "amount": 21.0})
    assert r.status_code == 202
    body = client.get("/metrics").text
    assert 'notifications_processed_total{type="order.created"}' in body
    assert 'http_requests_total{method="POST",path="/events",status="202"}' in body


def test_invalid_event_rejected():
    assert client.post("/events", json={"type": "x"}).status_code == 422


def test_metrics_include_latency_histogram():
    client.get("/health")
    assert "http_request_duration_seconds_bucket" in client.get("/metrics").text
