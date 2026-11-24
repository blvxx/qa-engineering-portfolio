import httpx
from fastapi.testclient import TestClient

from services.common.database import get_db
from services.payment_service.main import app, get_ledger_client


class FakeLedgerClient:
    def __init__(self, status_code=201):
        self.status_code = status_code
        self.calls = []

    def post(self, path, json):
        self.calls.append((path, json))
        return httpx.Response(
            self.status_code,
            json={"transfer_id": 41, "status": "posted", "duplicate": False},
            request=httpx.Request("POST", "http://ledger/transfers"),
        )


def configure_app(test_session_factory, fake_ledger):
    def override_get_db():
        db = test_session_factory()
        try:
            yield db
        finally:
            db.close()

    def override_ledger():
        yield fake_ledger

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_ledger_client] = override_ledger


def test_payment_calls_ledger_and_returns_posted(test_session_factory):
    ledger = FakeLedgerClient()
    configure_app(test_session_factory, ledger)
    try:
        with TestClient(app) as client:
            response = client.post("/payments", json={
                "idempotency_key": "payment-test-0001",
                "customer_account": "customer-10",
                "merchant_account": "merchant-10",
                "amount_minor": 12500,
                "currency": "RUB",
            })
            assert response.status_code == 201
            assert response.json()["status"] == "posted"
            assert response.json()["ledger_transfer_id"] == 41
            assert len(ledger.calls) == 1
            assert ledger.calls[0][0] == "/transfers"
    finally:
        app.dependency_overrides.clear()


def test_payment_idempotency_does_not_repeat_ledger_call(test_session_factory):
    ledger = FakeLedgerClient()
    configure_app(test_session_factory, ledger)
    try:
        with TestClient(app) as client:
            payload = {
                "idempotency_key": "payment-test-0002",
                "customer_account": "customer-20",
                "merchant_account": "merchant-20",
                "amount_minor": 500,
                "currency": "RUB",
            }
            first = client.post("/payments", json=payload)
            second = client.post("/payments", json=payload)
            assert first.status_code == second.status_code == 201
            assert second.json()["duplicate"] is True
            assert len(ledger.calls) == 1
    finally:
        app.dependency_overrides.clear()


def test_payment_rejects_idempotency_key_payload_conflict(test_session_factory):
    ledger = FakeLedgerClient()
    configure_app(test_session_factory, ledger)
    try:
        with TestClient(app) as client:
            payload = {
                "idempotency_key": "payment-test-0003",
                "customer_account": "customer-30",
                "merchant_account": "merchant-30",
                "amount_minor": 500,
                "currency": "RUB",
            }
            client.post("/payments", json=payload)
            conflict = client.post("/payments", json={**payload, "amount_minor": 800})
            assert conflict.status_code == 409
            assert len(ledger.calls) == 1
    finally:
        app.dependency_overrides.clear()


def test_payment_marks_failed_when_ledger_returns_error(test_session_factory):
    ledger = FakeLedgerClient(status_code=503)
    configure_app(test_session_factory, ledger)
    try:
        with TestClient(app) as client:
            response = client.post("/payments", json={
                "idempotency_key": "payment-test-0004",
                "customer_account": "customer-40",
                "merchant_account": "merchant-40",
                "amount_minor": 300,
                "currency": "RUB",
            })
            assert response.status_code == 502
            assert response.json()["detail"] == "Ledger service unavailable or rejected transfer"
    finally:
        app.dependency_overrides.clear()


def test_failed_payment_can_be_retried_safely(test_session_factory):
    ledger = FakeLedgerClient(status_code=503)
    configure_app(test_session_factory, ledger)
    try:
        with TestClient(app) as client:
            payload = {
                "idempotency_key": "payment-test-0006",
                "customer_account": "customer-60",
                "merchant_account": "merchant-60",
                "amount_minor": 1200,
                "currency": "RUB",
            }
            first = client.post("/payments", json=payload)
            assert first.status_code == 502

            ledger.status_code = 201
            retry = client.post("/payments", json=payload)
            assert retry.status_code == 201
            assert retry.json()["status"] == "posted"
            assert retry.json()["duplicate"] is True
            assert len(ledger.calls) == 2
    finally:
        app.dependency_overrides.clear()


def test_payment_rejects_invalid_amount_before_ledger_call(test_session_factory):
    ledger = FakeLedgerClient()
    configure_app(test_session_factory, ledger)
    try:
        with TestClient(app) as client:
            response = client.post("/payments", json={
                "idempotency_key": "payment-test-0005",
                "customer_account": "customer-50",
                "merchant_account": "merchant-50",
                "amount_minor": 0,
                "currency": "RUB",
            })
            assert response.status_code == 422
            assert ledger.calls == []
    finally:
        app.dependency_overrides.clear()
