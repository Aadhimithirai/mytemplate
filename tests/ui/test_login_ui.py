"""UI coverage for the login flow, driven through a real browser.

Marked ``ui`` so the backend suite can run without a browser installed:
    pytest -m "not ui"      backend only
    pytest -m ui            browser only
"""

import pytest
from playwright.sync_api import Page, expect

from tests.ui.conftest import UI_USER_EMAIL, UI_USER_PASSWORD

pytestmark = pytest.mark.ui


def test_visitor_can_log_in_and_see_the_dashboard(page: Page, live_server):
    """The core user-facing flow: land on /login, sign in, reach the dashboard."""
    page.goto(f"{live_server}/login", wait_until="domcontentloaded")

    expect(page).to_have_title("MyTemplate Login Example")
    expect(page.get_by_text("Login to your account")).to_be_visible()

    page.fill("#email", UI_USER_EMAIL)
    page.fill("#password", UI_USER_PASSWORD)
    page.click("button[type=submit]")

    expect(page.get_by_text("Logged in successfully.")).to_be_visible()

    page.goto(f"{live_server}/dashboard/", wait_until="domcontentloaded")

    # get_by_text("team Dashboard") is ambiguous - it also matches a nav
    # dropdown link and a debug-toolbar route row. Target the page heading.
    expect(page.locator("h1.page-title")).to_contain_text("team Dashboard")
    expect(page.locator(".card").get_by_text("New Tickets")).to_be_visible()


def test_wrong_password_keeps_the_visitor_on_the_login_page(page: Page, live_server):
    """A rejected login must not leak the visitor into the dashboard."""
    page.goto(f"{live_server}/login", wait_until="domcontentloaded")

    page.fill("#email", UI_USER_EMAIL)
    page.fill("#password", "not-the-password")
    page.click("button[type=submit]")

    expect(page.get_by_text("Login to your account")).to_be_visible()
    expect(page.get_by_text("Logged in successfully.")).not_to_be_visible()


def test_landing_page_uses_the_mytemplate_branding(page: Page, live_server):
    """The rename is visible to a real browser, not just in the HTML source."""
    page.goto(live_server, wait_until="domcontentloaded")

    expect(page).to_have_title("MyTemplate")
    expect(page.locator("header").get_by_text("MyTemplate")).to_be_visible()
