# OLAP / Cube extension design

> Design-only extension. Cube.js is not deployed in this portfolio release.

## Proposed semantic model

| Measure | Definition |
|---|---|
| Invoices.count | Count of unique invoice IDs |
| Invoices.amountTotal | Sum of amount in native currency; never combine currencies |
| Invoices.paidCount | Count where status = paid |
| Invoices.unpaidCount | Count where status = unpaid |
| Invoices.overdueCount | Count where status = overdue |

Dimensions: invoice date, status, currency and customer ID (customer-level dimension restricted to permitted roles).

## Contract test ideas

1. Compare Cube measure Invoices.count with SQL COUNT(DISTINCT invoice_id).
2. Compare each currency slice of Invoices.amountTotal with the DWH mart.
3. Validate filter semantics for invoice date and status.
4. Validate role-based access to customer-level dimensions.
5. Compare pre-aggregated and non-pre-aggregated query results.
6. Verify cache freshness after a new source batch.

## Example REST request (illustrative)

~~~json
{
  "measures": ["Invoices.count", "Invoices.amountTotal"],
  "dimensions": ["Invoices.currency", "Invoices.status"],
  "timeDimensions": [
    {
      "dimension": "Invoices.invoiceDate",
      "dateRange": ["2026-11-01", "2026-11-30"]
    }
  ]
}
~~~

A future implementation must run these checks against a real Cube API endpoint. This document alone does not demonstrate Cube REST API experience.
