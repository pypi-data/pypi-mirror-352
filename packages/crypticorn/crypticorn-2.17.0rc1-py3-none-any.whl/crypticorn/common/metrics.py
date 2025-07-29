# metrics/registry.py
from prometheus_client import (
    Counter, Gauge, Histogram, Summary, CollectorRegistry
)

registry = CollectorRegistry()

http_requests_total = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["method", "endpoint", "status_code"],
    registry=registry
)

http_request_duration_seconds = Histogram(
    "http_request_duration_seconds",
    "HTTP request duration in seconds",
    ["endpoint"],
    registry=registry
)