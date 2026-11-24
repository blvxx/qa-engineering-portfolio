import os

import httpx
from fastapi import Depends, FastAPI, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from services.common.database import Base, engine, get_db
from services.payment_service.models import Payment
from services.common.metrics import install_metrics

Base.metadata.create_all(bind=engine)

LEDGER_SERVICE_URL = os.getenv("LEDGER_SERVICE_URL", "http://127.0.0.1:8001")
app = FastAPI(title="Payment Service", version="1.0.0")
install_metrics(app, "payment")


class PaymentCreate(BaseModel):
    idempotency_key: str = Field(min_length=8, max_length=128)
    customer_account: str = Field(min_length=3, max_length=64)
    merchant_account: str = Field(min_length=3, max_length=64)
    amount_minor: int = Field(gt=0, le=100_000_000)
    currency: str = Field(default="RUB", pattern="^[A-Z]{3}$")


def get_ledger_client():
    with httpx.Client(base_url=LEDGER_SERVICE_URL, timeout=3.0) as client:
        yield client


@app.get("/health")
def health():
    return {"status": "ok", "service": "payment"}


@app.get("/health/ready")
def readiness(db: Session = Depends(get_db)):
    db.execute(text("SELECT 1"))
    return {"status": "ready", "database": "ok"}


@app.post("/payments", status_code=status.HTTP_201_CREATED)
def create_payment(
    payload: PaymentCreate,
    db: Session = Depends(get_db),
    ledger: httpx.Client = Depends(get_ledger_client),
):
    if payload.customer_account == payload.merchant_account:
        raise HTTPException(status_code=422, detail="Customer and merchant accounts must differ")

    payment = db.query(Payment).filter_by(idempotency_key=payload.idempotency_key).first()
    is_retry = payment is not None
    if payment:
        same_request = (
            payment.customer_account == payload.customer_account
            and payment.merchant_account == payload.merchant_account
            and payment.amount_minor == payload.amount_minor
            and payment.currency == payload.currency
        )
        if not same_request:
            raise HTTPException(status_code=409, detail="Idempotency key reused with different payload")
        if payment.status == "posted":
            return {
                "payment_id": payment.id,
                "status": payment.status,
                "ledger_transfer_id": payment.ledger_transfer_id,
                "duplicate": True,
            }
        # A previous attempt may have timed out after Ledger committed. Retry with
        # the same idempotency key so Ledger can safely return its original transfer.
    else:
        payment = Payment(**payload.model_dump(), status="pending")
        db.add(payment)
        db.commit()
        db.refresh(payment)

    try:
        response = ledger.post("/transfers", json={
            "idempotency_key": payload.idempotency_key,
            "from_account": payload.customer_account,
            "to_account": payload.merchant_account,
            "amount_minor": payload.amount_minor,
            "currency": payload.currency,
        })
        response.raise_for_status()
        ledger_result = response.json()
    except httpx.HTTPError as exc:
        payment.status = "failed"
        db.commit()
        raise HTTPException(status_code=502, detail="Ledger service unavailable or rejected transfer") from exc

    payment.status = "posted"
    payment.ledger_transfer_id = ledger_result["transfer_id"]
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail="Payment persistence conflict") from exc
    db.refresh(payment)

    return {
        "payment_id": payment.id,
        "status": payment.status,
        "ledger_transfer_id": payment.ledger_transfer_id,
        "duplicate": is_retry,
    }


@app.get("/payments/{payment_id}")
def get_payment(payment_id: int, db: Session = Depends(get_db)):
    payment = db.get(Payment, payment_id)
    if payment is None:
        raise HTTPException(status_code=404, detail="Payment not found")
    return {
        "payment_id": payment.id,
        "status": payment.status,
        "amount_minor": payment.amount_minor,
        "currency": payment.currency,
        "ledger_transfer_id": payment.ledger_transfer_id,
    }
