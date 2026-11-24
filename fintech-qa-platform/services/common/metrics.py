"""Prometheus metrics shared by the demo FastAPI services."""

from time import perf_counter

from fastapi import FastAPI, Request, Response
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest

HTTP_REQUESTS = Counter("http_requests_total", "Total HTTP requests handled by the service", ("service", "method", "route", "status"))
HTTP_DURATION = Histogram("http_request_duration_seconds", "HTTP request duration in seconds", ("service", "method", "route"), buckets=(0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1, 2.5, 5, 10))

def install_metrics(app: FastAPI, service_name: str) -> None:
    @app.middleware("http")
    async def observe_http_requests(request: Request, call_next):
        if request.url.path == "/metrics":
            return await call_next(request)
        started = perf_counter()
        status_code = 500
        try:
            response = await call_next(request)
            status_code = response.status_code
            return response
        finally:
            route = request.scope.get("route")
            route_name = getattr(route, "path", "unmatched")
            labels = (service_name, request.method, route_name)
            HTTP_REQUESTS.labels(*labels, str(status_code)).inc()
            HTTP_DURATION.labels(*labels).observe(perf_counter() - started)

    @app.get("/metrics", include_in_schema=False)
    def metrics_endpoint() -> Response:
        return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
