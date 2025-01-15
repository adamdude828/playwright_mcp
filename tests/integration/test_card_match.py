from playwright.sync_api import Page


def test_card_match_form(page: Page):
    # Navigate to the CardMatch page
    page.goto("https://thepointsguy.com/card-match/")
    
    # Wait for the form to be loaded
    page.wait_for_selector("form", state="visible")
    
    # Fill out the form
    page.fill("input[name='firstName']", "John")
    page.fill("input[name='lastName']", "Doe")
    page.fill("input[name='street']", "123 Main St")
    page.fill("input[name='city']", "New York")
    
    # Select state from dropdown
    page.select_option("select[name='State']", "NY")
    
    page.fill("input[name='zip']", "10001")
    page.fill("input[name='ssn']", "1234")
    page.fill("input[name='email']", "test@example.com")
    
    # Check newsletter subscription checkbox if present
    newsletter_checkbox = page.locator("#wantsNewsletterCm")
    if newsletter_checkbox.is_visible():
        newsletter_checkbox.check()
    
    # Set up a listener for network requests
    with page.expect_response(lambda response: "card-match" in response.url) as response_info:
        # Click the submit button
        submit_button = page.locator("button:has-text('Get matches')")
        submit_button.click()
    
    # Get the response
    response = response_info.value
    
    # Take a screenshot for debugging
    page.screenshot(path="form_submission_result.png")
    
    # Print response status for debugging
    print(f"Response status: {response.status}")
    
    # Assert that the response was successful
    assert response.ok, f"Form submission failed with status {response.status}"
    
    # Wait for any error messages that might appear
    error_messages = page.locator(".error-message, .alert-error")
    if error_messages.count() > 0:
        error_text = error_messages.first.text_content()
        raise AssertionError(f"Form submission showed error: {error_text}") 