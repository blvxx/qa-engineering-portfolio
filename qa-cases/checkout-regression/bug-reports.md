# Simulated Defect Reports

These are **hypothetical defects derived from test design**, not observed bugs in a real product. They demonstrate defect-reporting format and risk analysis.

## BUG-CHECK-01 — Double submission creates duplicate orders
- **Severity:** Critical (proposed)
- **Priority:** P0
- **Area:** Checkout
- **Precondition:** Valid cart and checkout data
- **Steps:** 1. Submit order. 2. Click submit again while the first request is pending.
- **Expected:** One order only; submit is protected and request is idempotent.
- **Hypothetical actual:** Two order confirmations/records are created.
- **Evidence:** Placeholder; would require a recording/network trace.
- **Status:** Hypothetical / Not verified.

## BUG-CART-02 — Discount is not recalculated after removing an item
- **Severity:** Major (proposed)
- **Priority:** P1
- **Steps:** Add eligible products; apply SAVE10; remove one eligible product.
- **Expected:** Discount recalculates against current eligible subtotal.
- **Hypothetical actual:** Discount retains previous amount.
- **Status:** Hypothetical / Not verified.

## BUG-SHIP-03 — Shipping fee persists after changing delivery method
- **Severity:** Major (proposed)
- **Priority:** P1
- **Steps:** Select paid delivery; switch to pickup.
- **Expected:** Shipping fee becomes zero for pickup.
- **Hypothetical actual:** Old fee remains in order total.
- **Status:** Hypothetical / Not verified.

## BUG-FORM-04 — Invalid email accepted by checkout
- **Severity:** Major (proposed)
- **Priority:** P1
- **Steps:** Enter malformed email; submit checkout.
- **Expected:** Validation blocks submission with actionable message.
- **Hypothetical actual:** Order is accepted.
- **Status:** Hypothetical / Not verified.
