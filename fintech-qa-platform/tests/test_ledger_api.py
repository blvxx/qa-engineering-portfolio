from fastapi.testclient import TestClient

from services.common.database import get_db
from services.ledger_service.main import app


def configure_db(test_session_factory):
    def override_get_db():
        db = test_session_factory()
        try:
            yield db
        finally:
            db.close()
    app.dependency_overrides[get_db] = override_get_db


def test_transfer_creates_balanced_ledger_entries(test_session_factory):
    configure_db(test_session_factory)
    try:
        with TestClient(app) as client:
            payload = {
                "idempotency_key": "ledger-test-0001",
                "from_account": "customer-01",
                "to_account": "merchant-01",
                "amount_minor": 2500,
                "currency": "RUB",
            }
            created = client.post("/transfers", json=payload)
            assert created.status_code == 201
            assert created.json()["duplicate"] is False
            debit = client.get("/accounts/customer-01/balance")
            credit = client.get("/accounts/merchant-01/balance")
            assert debit.json()["balance_minor"] == -2500
            assert credit.json()["balance_minor"] == 2500
            assert debit.json()["balance_minor"] + credit.json()["balance_minor"] == 0
    finally:
        app.dependency_overrides.clear()


def test_transfer_is_idempotent_and_conflicting_reuse_is_rejected(test_session_factory):
    configure_db(test_session_factory)
    try:
        with TestClient(app) as client:
            payload = {
                "idempotency_key": "ledger-test-0002",
                "from_account": "customer-02",
                "to_account": "merchant-02",
                "amount_minor": 700,
                "currency": "RUB",
            }
            first = client.post("/transfers", json=payload)
            second = client.post("/transfers", json=payload)
            assert first.status_code == second.status_code == 201
            assert second.json()["duplicate"] is True
            conflict = client.post("/transfers", json={**payload, "amount_minor": 900})
            assert conflict.status_code == 409
            balance = client.get("/accounts/customer-02/balance")
            assert balance.json()["balance_minor"] == -700
    finally:
        app.dependency_overrides.clear()


def test_transfer_rejects_same_account(test_session_factory):
    configure_db(test_session_factory)
    try:
        with TestClient(app) as client:
            response = client.post("/transfers", json={
                "idempotency_key": "ledger-test-0003",
                "from_account": "same-account",
                "to_account": "same-account",
                "amount_minor": 100,
                "currency": "RUB",
            })
            assert response.status_code == 422
    finally:
        app.dependency_overrides.clear()
