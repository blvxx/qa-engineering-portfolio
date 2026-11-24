from playwright.sync_api import Page, expect


def add_product(page: Page, name: str = "Basic") -> None:
    page.get_by_role("button", name=f"Add {name}").click()


def fill_valid_checkout(page: Page, *, pickup: bool = False) -> None:
    page.get_by_label("Full name").fill("Alex Morgan")
    page.get_by_label("Email address").fill("alex@example.com")
    if not pickup:
        page.get_by_label("Delivery address").fill("10 Market Street")
    else:
        page.get_by_label("Fulfilment method").select_option("pickup")


def test_catalogue_renders_stock_and_price(page: Page) -> None:
    expect(page.get_by_role("heading", name="Featured products")).to_be_visible()
    expect(page.locator("[data-product-id='basic']")).to_contain_text("CU 100.00")
    expect(page.get_by_role("button", name="Unavailable")).to_be_disabled()


def test_add_product_creates_cart_line_and_subtotal(page: Page) -> None:
    add_product(page)
    expect(page.get_by_test_id("cart-item")).to_have_count(1)
    expect(page.get_by_test_id("subtotal")).to_have_text("CU 100.00")


def test_quantity_increase_recalculates_line_and_subtotal(page: Page) -> None:
    add_product(page)
    page.get_by_role("button", name="Increase quantity for Basic").click()
    expect(page.get_by_test_id("quantity-basic")).to_have_text("2")
    expect(page.get_by_test_id("subtotal")).to_have_text("CU 200.00")


def test_quantity_decrease_does_not_allow_zero(page: Page) -> None:
    add_product(page)
    page.get_by_role("button", name="Decrease quantity for Basic").click()
    expect(page.get_by_test_id("cart-item")).to_have_count(0)
    expect(page.get_by_test_id("subtotal")).to_have_text("CU 0.00")


def test_remove_item_recalculates_summary(page: Page) -> None:
    add_product(page)
    page.get_by_role("button", name="Remove Basic").click()
    expect(page.get_by_test_id("cart-item")).to_have_count(0)
    expect(page.get_by_test_id("total")).to_have_text("CU 0.00")


def test_stock_limit_disables_quantity_increase(page: Page) -> None:
    add_product(page)
    for _ in range(9):
        page.get_by_role("button", name="Increase quantity for Basic").click()
    expect(page.get_by_test_id("quantity-basic")).to_have_text("10")
    expect(page.get_by_role("button", name="Increase quantity for Basic")).to_be_disabled()


def test_zero_stock_product_cannot_be_added(page: Page) -> None:
    expect(page.get_by_role("button", name="Unavailable")).to_be_disabled()
    expect(page.get_by_test_id("cart-item")).to_have_count(0)


def test_valid_promo_applies_ten_percent_discount(page: Page) -> None:
    add_product(page)
    page.get_by_label("Promo code").fill("SAVE10")
    page.get_by_role("button", name="Apply code").click()
    expect(page.get_by_test_id("discount")).to_have_text("− CU 10.00")
    expect(page.get_by_test_id("total")).to_have_text("CU 110.00")


def test_expired_promo_is_rejected_without_discount(page: Page) -> None:
    add_product(page)
    page.get_by_label("Promo code").fill("EXPIRED")
    page.get_by_role("button", name="Apply code").click()
    expect(page.get_by_role("status").filter(has_text="expired")).to_be_visible()
    expect(page.get_by_test_id("discount")).to_have_text("− CU 0.00")


def test_unknown_promo_is_rejected(page: Page) -> None:
    add_product(page)
    page.get_by_label("Promo code").fill("NOTREAL")
    page.get_by_role("button", name="Apply code").click()
    expect(page.get_by_role("status").filter(has_text="not recognised")).to_be_visible()


def test_applying_same_promo_twice_does_not_duplicate_discount(page: Page) -> None:
    add_product(page)
    page.get_by_label("Promo code").fill("SAVE10")
    page.get_by_role("button", name="Apply code").click()
    page.get_by_role("button", name="Apply code").click()
    expect(page.get_by_test_id("discount")).to_have_text("− CU 10.00")


def test_discount_recalculates_after_cart_quantity_change(page: Page) -> None:
    add_product(page)
    page.get_by_label("Promo code").fill("SAVE10")
    page.get_by_role("button", name="Apply code").click()
    page.get_by_role("button", name="Increase quantity for Basic").click()
    expect(page.get_by_test_id("discount")).to_have_text("− CU 20.00")
    expect(page.get_by_test_id("total")).to_have_text("CU 200.00")


def test_delivery_fee_is_included_in_total(page: Page) -> None:
    add_product(page)
    expect(page.get_by_test_id("shipping")).to_have_text("CU 20.00")
    expect(page.get_by_test_id("total")).to_have_text("CU 120.00")


def test_switching_to_pickup_removes_delivery_fee(page: Page) -> None:
    add_product(page)
    page.get_by_label("Fulfilment method").select_option("pickup")
    expect(page.get_by_test_id("shipping")).to_have_text("CU 0.00")
    expect(page.get_by_test_id("total")).to_have_text("CU 100.00")


def test_switching_fulfilment_does_not_accumulate_shipping(page: Page) -> None:
    add_product(page)
    method = page.get_by_label("Fulfilment method")
    method.select_option("pickup")
    method.select_option("delivery")
    method.select_option("pickup")
    expect(page.get_by_test_id("shipping")).to_have_text("CU 0.00")


def test_checkout_requires_customer_name_and_email(page: Page) -> None:
    add_product(page)
    page.get_by_role("button", name="Place order").click()
    expect(page.locator("#customer-name")).to_have_js_property("validity.valid", False)
    expect(page.locator("#email")).to_have_js_property("validity.valid", False)
    expect(page.locator("#order-confirmation")).to_be_hidden()


def test_checkout_rejects_invalid_email(page: Page) -> None:
    add_product(page)
    page.get_by_label("Full name").fill("Alex Morgan")
    page.get_by_label("Email address").fill("not-an-email")
    page.get_by_label("Delivery address").fill("10 Market Street")
    page.get_by_role("button", name="Place order").click()
    expect(page.locator("#email")).to_have_js_property("validity.valid", False)
    expect(page.locator("#order-confirmation")).to_be_hidden()


def test_delivery_address_is_required_for_delivery(page: Page) -> None:
    add_product(page)
    page.get_by_label("Full name").fill("Alex Morgan")
    page.get_by_label("Email address").fill("alex@example.com")
    page.get_by_role("button", name="Place order").click()
    expect(page.locator("#address")).to_have_js_property("validity.valid", False)


def test_pickup_does_not_require_delivery_address(page: Page) -> None:
    add_product(page)
    fill_valid_checkout(page, pickup=True)
    expect(page.locator("#address")).to_have_js_property("required", False)
    page.get_by_role("button", name="Place order").click()
    expect(page.locator("#order-confirmation")).to_be_visible()


def test_successful_checkout_displays_order_reference(page: Page) -> None:
    add_product(page)
    fill_valid_checkout(page)
    page.get_by_role("button", name="Place order").click()
    expect(page.get_by_role("heading", name="Thank you. Your test order is confirmed.")).to_be_visible()
    expect(page.locator("#order-reference")).to_have_text("NS-00001")


def test_rapid_duplicate_submit_creates_only_one_order(page: Page) -> None:
    add_product(page)
    fill_valid_checkout(page)
    page.evaluate("""() => {
      const button = document.querySelector('#place-order');
      button.click();
      button.click();
    }""")
    expect(page.get_by_test_id("orders-created")).to_have_text("1")
    expect(page.locator("#order-confirmation")).to_be_visible()


def test_checkout_layout_has_no_horizontal_overflow_on_mobile(page: Page) -> None:
    page.set_viewport_size({"width": 375, "height": 812})
    add_product(page)
    metrics = page.evaluate("({width: document.documentElement.clientWidth, scroll: document.documentElement.scrollWidth})")
    assert metrics["scroll"] <= metrics["width"]


def test_required_inputs_have_programmatic_labels(page: Page) -> None:
    for selector in ("#customer-name", "#email", "#fulfilment", "#address"):
        assert page.locator(selector).evaluate("el => Boolean(el.labels && el.labels.length)")

def test_discount_recalculates_after_removing_eligible_product(page: Page) -> None:
    add_product(page, "Basic")
    add_product(page, "Premium")
    page.get_by_label("Promo code").fill("SAVE10")
    page.get_by_role("button", name="Apply code").click()
    expect(page.get_by_test_id("discount")).to_have_text("− CU 35.00")
    page.get_by_role("button", name="Remove Premium").click()
    expect(page.get_by_test_id("subtotal")).to_have_text("CU 100.00")
    expect(page.get_by_test_id("discount")).to_have_text("− CU 10.00")
    expect(page.get_by_test_id("total")).to_have_text("CU 110.00")
