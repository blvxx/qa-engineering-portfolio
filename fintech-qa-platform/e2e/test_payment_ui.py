import time
from pathlib import Path

import allure
from playwright.sync_api import Page, expect


@allure.epic("FinTech QA Platform")
@allure.feature("Payment UI")
class TestPaymentUI:
    @allure.story("Successful payment and balance verification")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_customer_can_create_payment_and_check_balance(self, page: Page, base_url: str):
        customer = f"ui-customer-{time.time_ns()}"
        merchant = f"ui-merchant-{time.time_ns()}"
        idempotency_key = f"ui-payment-{time.time_ns()}"

        page.goto(base_url)
        expect(page.get_by_role("heading", name="Payment operations")).to_be_visible()

        page.locator("#idempotency-key").fill(idempotency_key)
        page.locator("#customer-account").fill(customer)
        page.locator("#merchant-account").fill(merchant)
        page.locator("#amount").fill("1250")
        page.get_by_role("button", name="Submit payment").click()

        result = page.locator("#payment-result")
        expect(result).to_contain_text("Payment posted")
        expect(result).to_have_attribute("data-state", "success")

        page.locator("#account-id").fill(customer)
        page.get_by_role("button", name="Check balance").click()
        balance = page.locator("#balance-result")
        expect(balance).to_have_text("Balance: -1250 RUB")
        expect(balance).to_have_attribute("data-state", "success")

        screenshot = Path("docs/screenshots/payment-ui.png")
        screenshot.parent.mkdir(parents=True, exist_ok=True)
        page.screenshot(path=str(screenshot), full_page=True)
        allure.attach.file(
            str(screenshot),
            name="Payment UI — successful payment and balance",
            attachment_type=allure.attachment_type.PNG,
        )

    @allure.story("Client-side validation")
    @allure.severity(allure.severity_level.NORMAL)
    def test_payment_form_rejects_zero_amount(self, page: Page, base_url: str):
        page.goto(base_url)
        page.locator("#amount").fill("0")
        page.get_by_role("button", name="Submit payment").click()

        expect(page.locator("#amount")).to_have_js_property("validity.valid", False)
        expect(page.locator("#payment-result")).to_be_empty()
