# Test Plan — Checkout & Cart Quality Engineering

## 1. Objective
Protect the critical customer purchase path against pricing, stock, promotion, fulfilment, validation and duplicate-submission regressions.

## 2. System under test
Northstar Market is an authored static storefront created solely as a deterministic QA target. It uses a fixed in-memory product catalogue and simulated order confirmation. It does not contact payment, inventory, shipping or customer systems.

## 3. Scope and risk model

| Area | Main risk | Priority |
|---|---|---|
| Cart quantity and stock | Oversell or incorrect line totals | P0 / P1 |
| Discount calculation | Customer charged incorrectly | P0 |
| Shipping selection | Incorrect final amount | P1 |
| Required checkout data | Invalid or incomplete order accepted | P1 |
| Duplicate submission | Duplicate order creation | P0 |
| Responsive layout and labels | Checkout unusable on common devices / assistive tech | P2 |

## 4. Test levels and techniques
- Playwright browser UI automation for end-to-end user flows.
- Positive, negative and boundary-value testing.
- State-transition testing across cart, promo and fulfilment changes.
- Calculation assertions at subtotal, discount, shipping and total levels.
- Native browser form-validity checks.
- Responsive viewport and accessible-label smoke checks.

## 5. Test data
| Product | Unit price | Available stock | Promo eligible |
|---|---:|---:|---|
| Basic | CU 100.00 | 10 | Yes |
| Premium | CU 250.00 | 3 | Yes |
| Gift item | CU 25.00 | 0 | No |

- `SAVE10`: 10% off eligible products.
- `EXPIRED`: expired promo.
- Any other value: unknown promo.
- Standard delivery: CU 20.00; store pickup: free.

## 6. Automation and reproducibility
The pytest fixture reads the app's HTML, CSS and JavaScript from the repository and loads it into a fresh Chromium page. Each test receives a new browser context and clean page state. Playwright traces are written for every test; screenshots are captured for failed tests.

## 7. Exit criteria
- All P0 and P1 automated tests pass.
- No unexpected browser page errors.
- Test report and trace artifacts are retained by CI.
- Responsive smoke and programmatic-label checks pass.

## 8. Known limitations
This sandbox does not validate backend persistence, payment gateway behavior, inventory concurrency across sessions, real network failures, cross-browser rendering or production analytics. Those require a real application and test environment.
