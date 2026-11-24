"""Deterministic transport tests using a loopback HTTP server only."""

from __future__ import annotations

from contextlib import contextmanager
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from threading import Thread
from typing import Iterator

import pytest

from api_client import PostsApiClient


pytestmark = pytest.mark.transport


class FaultInjectingHandler(BaseHTTPRequestHandler):
    get_attempts = 0
    post_attempts = 0

    def do_GET(self) -> None:
        type(self).get_attempts += 1
        status = 503 if type(self).get_attempts == 1 else 200
        body = b'{"error":"temporary"}' if status == 503 else b"[]"
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self) -> None:
        type(self).post_attempts += 1
        body = b'{"error":"temporary"}'
        self.send_response(503)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format: str, *args: object) -> None:
        return


@contextmanager
def local_api() -> Iterator[str]:
    FaultInjectingHandler.get_attempts = 0
    FaultInjectingHandler.post_attempts = 0
    server = ThreadingHTTPServer(("127.0.0.1", 0), FaultInjectingHandler)
    server.daemon_threads = True
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        host, port = server.server_address
        yield f"http://{host}:{port}"
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)


def test_retries_safe_reads_but_never_replays_write_requests() -> None:
    with local_api() as base_url:
        with PostsApiClient(
            base_url=base_url,
            max_retries=1,
            backoff_factor=0,
            timeout=2,
        ) as client:
            read_response = client.get_posts()
            write_response = client.create_post(
                {"userId": 1, "title": "Retry boundary", "body": "local test"}
            )

        assert read_response.status_code == 200
        assert FaultInjectingHandler.get_attempts == 2
        assert write_response.status_code == 503
        assert FaultInjectingHandler.post_attempts == 1
