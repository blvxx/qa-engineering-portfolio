from __future__ import annotations

from pathlib import Path
import os
from shutil import which

import pytest
from playwright.sync_api import Browser, Page, sync_playwright

ROOT = Path(__file__).parent
APP_DIR = ROOT / "app"
RESULTS_DIR = ROOT / "test-results"


@pytest.fixture(scope="session")
def browser() -> Browser:
    with sync_playwright() as playwright:
        executable = os.getenv("PLAYWRIGHT_CHROMIUM_EXECUTABLE") or which("chromium")
        launch_options = {"headless": True, "args": ["--no-sandbox"]}
        if executable:
            launch_options["executable_path"] = executable
        instance = playwright.chromium.launch(**launch_options)
        yield instance
        instance.close()


@pytest.fixture
def page(browser: Browser, request: pytest.FixtureRequest) -> Page:
    RESULTS_DIR.mkdir(exist_ok=True)
    context = browser.new_context(viewport={"width": 1365, "height": 900})
    context.tracing.start(screenshots=True, snapshots=True, sources=True)
    page = context.new_page()
    html = (APP_DIR / "index.html").read_text(encoding="utf-8")
    css = (APP_DIR / "styles.css").read_text(encoding="utf-8")
    js = (APP_DIR / "app.js").read_text(encoding="utf-8")
    html = html.replace('<link rel="stylesheet" href="styles.css">', f"<style>{css}</style>")
    html = html.replace('<script src="app.js" defer></script>', "")
    html = html.replace("</body>", f"<script>{js}</script></body>")
    page.set_content(html, wait_until="load")
    yield page

    safe_name = request.node.name.replace("/", "_")
    context.tracing.stop(path=str(RESULTS_DIR / f"{safe_name}.zip"))
    if hasattr(request.node, "rep_call") and request.node.rep_call.failed:
        page.screenshot(path=str(RESULTS_DIR / f"{safe_name}.png"), full_page=True)
    context.close()


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item: pytest.Item, call: pytest.CallInfo):
    outcome = yield
    report = outcome.get_result()
    setattr(item, f"rep_{report.when}", report)
