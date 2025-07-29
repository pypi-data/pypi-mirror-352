import time
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from crypticorn.common.logging import configure_logging
from contextlib import asynccontextmanager
from typing_extensions import deprecated
import warnings
from crypticorn.common.warnings import CrypticornDeprecatedSince217
from crypticorn.common.metrics import http_requests_total, http_request_duration_seconds

class PrometheusMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        start = time.perf_counter()
        response = await call_next(request)
        duration = time.perf_counter() - start

        http_requests_total.labels(
            method=request.method,
            endpoint=request.url.path,
            status_code=response.status_code
        ).inc()

        http_request_duration_seconds.labels(
            endpoint=request.url.path
        ).observe(duration)

        return response


@deprecated("Use add_middleware instead", category=None)
def add_cors_middleware(app: "FastAPI"):
    warnings.warn("add_cors_middleware is deprecated. Use add_middleware instead.", CrypticornDeprecatedSince217)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:5173",  # vite dev server
            "http://localhost:4173",  # vite preview server
        ],
        allow_origin_regex="^https://([a-zA-Z0-9-]+.)*crypticorn.(dev|com)/?$",  # matches (multiple or no) subdomains of crypticorn.dev and crypticorn.com
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

def add_middleware(app: "FastAPI"):
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:5173",  # vite dev server
            "http://localhost:4173",  # vite preview server
        ],
        allow_origin_regex="^https://([a-zA-Z0-9-]+.)*crypticorn.(dev|com)/?$",  # matches (multiple or no) subdomains of crypticorn.dev and crypticorn.com
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(PrometheusMiddleware)


@asynccontextmanager
async def default_lifespan(app: FastAPI):
    """Default lifespan for the applications.
    This is used to configure the logging for the application.
    To override this, pass a different lifespan to the FastAPI constructor or call this lifespan within a custom lifespan.
    """
    configure_logging()
    yield
