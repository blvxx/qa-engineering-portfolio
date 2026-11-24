from quality_rules import is_reconciled, validate_source_rows

def valid_row(**changes):
    row = {
        "invoice_id": "INV-1", "customer_id": "CUST-1",
        "invoice_date": "2026-11-01", "amount": "100.00",
        "currency": "RUB", "status": "paid",
    }
    row.update(changes)
    return row

def test_valid_source_row_has_no_findings():
    assert validate_source_rows([valid_row()]) == []

def test_duplicate_invoice_id_is_detected():
    findings = validate_source_rows([valid_row(), valid_row()])
    assert any(item["rule_id"] == "DQ-002" for item in findings)

def test_missing_customer_is_detected():
    findings = validate_source_rows([valid_row(customer_id=" ")])
    assert any(item["rule_id"] == "DQ-003" for item in findings)

def test_non_positive_amount_is_detected():
    findings = validate_source_rows([valid_row(amount="0")])
    assert any(item["rule_id"] == "DQ-004" for item in findings)

def test_invalid_currency_and_status_are_detected():
    findings = validate_source_rows([valid_row(currency="BTC", status="unknown")])
    assert sum(item["rule_id"] == "DQ-005" for item in findings) == 2

def test_reconciliation_compares_counts():
    assert is_reconciled(10, 10)
    assert not is_reconciled(10, 9)
