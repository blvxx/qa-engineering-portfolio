from fastapi import Depends, FastAPI, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy import func, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from services.common.database import Base, engine, get_db
from services.ledger_service.models import LedgerEntry, LedgerTransfer
from services.common.metrics import install_metrics

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Ledger Service", version="1.0.0")
install_metrics(app, "ledger")


class TransferCreate(BaseModel):
    idempotency_key: str = Field(min_length=8, max_length=128)
    from_account: str = Field(min_length=3, max_length=64)
    to_account: str = Field(min_length=3, max_length=64)
    amount_minor: int = Field(gt=0, le=100_000_000)
    currency: str = Field(default="RUB", pattern="^[A-Z]{3}$")


@app.get("/health")
def health():
    return {"status": "ok", "service": "ledger"}


@app.get("/health/ready")
def readiness(db: Session = Depends(get_db)):
    db.execute(text("SELECT 1"))
    return {"status": "ready", "database": "ok"}


@app.post("/transfers", status_code=status.HTTP_201_CREATED)
def create_transfer(payload: TransferCreate, db: Session = Depends(get_db)):
    if payload.from_account == payload.to_account:
        raise HTTPException(status_code=422, detail="Source and destination accounts must differ")

    existing = db.query(LedgerTransfer).filter_by(
        idempotency_key=payload.idempotency_key
    ).first()
    if existing:
        same_request = (
            existing.from_account == payload.from_account
            and existing.to_account == payload.to_account
            and existing.amount_minor == payload.amount_minor
            and existing.currency == payload.currency
        )
        if not same_request:
            raise HTTPException(status_code=409, detail="Idempotency key reused with different payload")
        return {"transfer_id": existing.id, "status": "posted", "duplicate": True}

    transfer = LedgerTransfer(**payload.model_dump())
    db.add(transfer)
    db.flush()
    db.add_all([
        LedgerEntry(
            transfer_id=transfer.id,
            account_id=payload.from_account,
            amount_minor=-payload.amount_minor,
            currency=payload.currency,
        ),
        LedgerEntry(
            transfer_id=transfer.id,
            account_id=payload.to_account,
            amount_minor=payload.amount_minor,
            currency=payload.currency,
        ),
    ])
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail="Transfer idempotency conflict") from exc

    return {"transfer_id": transfer.id, "status": "posted", "duplicate": False}


@app.get("/accounts/{account_id}/balance")
def get_balance(account_id: str, currency: str = "RUB", db: Session = Depends(get_db)):
    balance = db.query(func.coalesce(func.sum(LedgerEntry.amount_minor), 0)).filter_by(
        account_id=account_id, currency=currency
    ).scalar()
    return {"account_id": account_id, "currency": currency, "balance_minor": int(balance)}
