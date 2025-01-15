import pytest
from playwright.sync_api import Page, expect


@pytest.fixture(scope="function", autouse=True)
def setup_function():
    # Add any setup code here
    pass


def test_basic_navigation(page: Page):
    """
    Example test demonstrating basic Playwright functionality.
    """
    # Navigate to a website
    page.goto("https://example.com")
    
    # Basic assertions
    expect(page).to_have_title("Example Domain")
    
    # Example of interacting with elements
    heading = page.locator("h1")
    expect(heading).to_have_text("Example Domain")
    
    # Example of taking a screenshot
    page.screenshot(path="tests/playwright/screenshots/example.png")


def test_form_interaction(page: Page):
    """
    Example test demonstrating form interactions.
    """
    # Navigate to a test site with a form
    page.goto("https://example.com")
    
    # Example form interactions (commented out as example.com doesn't have a form)
    # page.fill("input[name='search']", "test query")
    # page.click("button[type='submit']")
    
    # Wait for network idle (useful after form submissions)
    page.wait_for_load_state("networkidle") 