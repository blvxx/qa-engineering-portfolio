import pytest

from scripts.incident_drill import parse_prometheus_target, validate_local_url


def test_fault_drill_accepts_loopback_http_urls():
    validate_local_url("http://localhost:8000")
    validate_local_url("http://127.0.0.1:9090")
    validate_local_url("http://[::1]:8001")


@pytest.mark.parametrize(
    "url",
    [
        "https://localhost:8000",
        "http://example.com:8000",
        "http://192.168.1.10:8000",
        "file:///etc/passwd",
    ],
)
def test_fault_drill_rejects_non_loopback_urls(url):
    with pytest.raises(ValueError, match="localhost or loopback"):
        validate_local_url(url)


def test_prometheus_target_parser_reads_up_and_down_values():
    assert parse_prometheus_target(
        {"data": {"result": [{"metric": {"job": "ledger-service"}, "value": [0, "1"]}]}}
    ) is True
    assert parse_prometheus_target(
        {"data": {"result": [{"metric": {"job": "ledger-service"}, "value": [0, "0"]}]}}
    ) is False


def test_prometheus_target_parser_returns_none_when_target_is_missing():
    assert parse_prometheus_target({"data": {"result": []}}) is None
