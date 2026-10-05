"""Notification service: receives events over HTTP and exposes Prometheus metrics."""
import logging
import time

from fastapi import FastAPI, HTTPException, Request, Response
from prometheus_client import (CONTENT_TYPE_LATEST, Counter, Histogram,
                               generate_latest)
from pydantic import BaseModel

log = logging.getLogger("notification-service")

app = FastAPI(title="notification-service")

HTTP_REQUESTS = Counter("http_requests_total", "HTTP requests",
                        ["method", "path", "status"])
HTTP_ERRORS = Counter("http_errors_total", "HTTP 5xx responses", ["path"])
HTTP_LATENCY = Histogram("http_request_duration_seconds", "HTTP request latency",
                         ["method", "path"])
NOTIFICATIONS = Counter("notifications_processed_total",
                        "Notifications processed", ["type"])


class Event(BaseModel):
    type: str
    order_id: str
    customer: str
    amount: float = 0


@app.middleware("http")
async def instrument(request: Request, call_next):
    start = time.perf_counter()
    status = 500
    try:
        response = await call_next(request)
        status = response.status_code
        return response
    finally:
        # Use the route template to keep label cardinality bounded.
        route = request.scope.get("route")
        path = route.path if route else "unmatched"
        HTTP_LATENCY.labels(request.method, path).observe(time.perf_counter() - start)
        HTTP_REQUESTS.labels(request.method, path, str(status)).inc()
        if status >= 500:
            HTTP_ERRORS.labels(path).inc()


@app.get("/health")
def health():
    return {"status": "UP"}


@app.post("/events", status_code=202)
def receive_event(event: Event):
    if not event.type:
        raise HTTPException(status_code=422, detail="type required")
    log.info("notify customer=%s type=%s order=%s amount=%s",
             event.customer, event.type, event.order_id, event.amount)
    NOTIFICATIONS.labels(event.type).inc()
    return {"accepted": True}


@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
