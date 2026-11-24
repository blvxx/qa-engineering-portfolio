# Checkout Regression Test Catalogue

The following 24 Playwright tests execute against the local Northstar Market QA sandbox. The test names map directly to `tests/test_checkout.py`.

| ID | Priority | Scenario | Automated test |
|---|---|---|---|
| CAT-001 | P2 | Product catalogue, price and unavailable stock render | `test_catalogue_renders_stock_and_price` |
| CART-001 | P1 | Add product and verify cart line/subtotal | `test_add_product_creates_cart_line_and_subtotal` |
| CART-002 | P1 | Increase quantity recalculates line and subtotal | `test_quantity_increase_recalculates_line_and_subtotal` |
| CART-003 | P1 | Decrease quantity at one removes line, never creates zero | `test_quantity_decrease_does_not_allow_zero` |
| CART-004 | P1 | Remove item recalculates total | `test_remove_item_recalculates_summary` |
| CART-005 | P1 | Quantity cannot exceed available stock | `test_stock_limit_disables_quantity_increase` |
| CART-006 | P1 | Zero-stock item cannot be added | `test_zero_stock_product_cannot_be_added` |
| PROMO-001 | P0 | Valid promo applies 10% discount | `test_valid_promo_applies_ten_percent_discount` |
| PROMO-002 | P1 | Expired promo rejected | `test_expired_promo_is_rejected_without_discount` |
| PROMO-003 | P1 | Unknown promo rejected | `test_unknown_promo_is_rejected` |
| PROMO-004 | P1 | Reapplying promo does not duplicate discount | `test_applying_same_promo_twice_does_not_duplicate_discount` |
| PROMO-005 | P0 | Discount recalculates after quantity change | `test_discount_recalculates_after_cart_quantity_change` |
| PROMO-006 | P0 | Discount recalculates after removing an eligible item | `test_discount_recalculates_after_removing_eligible_product` |
| SHIP-001 | P1 | Delivery fee included in total | `test_delivery_fee_is_included_in_total` |
| SHIP-002 | P1 | Pickup removes delivery fee | `test_switching_to_pickup_removes_delivery_fee` |
| SHIP-003 | P1 | Switching fulfilment never accumulates fees | `test_switching_fulfilment_does_not_accumulate_shipping` |
| FORM-001 | P1 | Name and email are required | `test_checkout_requires_customer_name_and_email` |
| FORM-002 | P1 | Invalid email rejected | `test_checkout_rejects_invalid_email` |
| FORM-003 | P1 | Delivery address required for delivery | `test_delivery_address_is_required_for_delivery` |
| FORM-004 | P1 | Pickup does not require delivery address | `test_pickup_does_not_require_delivery_address` |
| ORDER-001 | P0 | Valid checkout displays a unique order reference | `test_successful_checkout_displays_order_reference` |
| ORDER-002 | P0 | Rapid repeated submit creates only one order | `test_rapid_duplicate_submit_creates_only_one_order` |
| UX-001 | P2 | Mobile viewport has no horizontal overflow | `test_checkout_layout_has_no_horizontal_overflow_on_mobile` |
| A11Y-001 | P2 | Required form controls have programmatic labels | `test_required_inputs_have_programmatic_labels` |

## Execution contract
Each test starts with a fresh page. No scenario relies on the state left by a previous test. Expected totals include the CU 20.00 delivery fee unless store pickup is selected.
