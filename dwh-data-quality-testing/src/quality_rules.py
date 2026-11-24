from collections import Counter
from decimal import Decimal

ALLOWED_CURRENCIES = {"RUB", "EUR", "USD"}
ALLOWED_STATUSES = {"paid", "unpaid", "overdue"}

def validate_source_rows(rows):
    """Return deterministic DQ findings for invoice source dictionaries."""
    findings = []
    ids = [str(row.get("invoice_id") or "").strip() for row in rows]
    duplicates = sorted(key for key, count in Counter(ids).items() if key and count > 1)
    if duplicates:
        findings.append({"rule_id": "DQ-002", "status": "FAIL", "details": f"Duplicate invoice IDs: {duplicates}"})
    for index, row in enumerate(rows, start=1):
        if not str(row.get("invoice_id") or "").strip() or not str(row.get("customer_id") or "").strip():
            findings.append({"rule_id": "DQ-003", "status": "FAIL", "details": f"Missing required identifier at row {index}"})
        try:
            amount = Decimal(str(row.get("amount")))
            if amount <= 0:
                findings.append({"rule_id": "DQ-004", "status": "FAIL", "details": f"Non-positive amount at row {index}"})
        except Exception:
            findings.append({"rule_id": "DQ-004", "status": "FAIL", "details": f"Invalid amount at row {index}"})
        if str(row.get("currency") or "").upper() not in ALLOWED_CURRENCIES:
            findings.append({"rule_id": "DQ-005", "status": "FAIL", "details": f"Unsupported currency at row {index}"})
        if str(row.get("status") or "").lower() not in ALLOWED_STATUSES:
            findings.append({"rule_id": "DQ-005", "status": "FAIL", "details": f"Unsupported status at row {index}"})
    return findings

def is_reconciled(source_count, target_count):
    return source_count == target_count
