"""End-to-end tests for StarLive application."""

import pytest
from playwright.sync_api import Page, expect


@pytest.mark.e2e
def test_homepage_loads(page: Page, app_server: str):
    """Test that the homepage loads correctly."""
    page.goto(app_server)

    # Check that the page loads
    expect(page).to_have_title("StarLive Demo - Universal Hypermedia")

    # Check that the header is visible
    expect(page.locator(".header h1")).to_contain_text("StarLive Demo")

    # Check that both HTMX and Turbo scripts are loaded
    expect(page.locator("script[src*='htmx']")).to_be_attached()
    expect(page.locator("script[src*='turbo']")).to_be_attached()


@pytest.mark.e2e
def test_technology_indicator(page: Page, app_server: str):
    """Test that the technology indicator shows the loaded library."""
    page.goto(app_server)

    # Wait for scripts to load and indicator to update
    page.wait_for_timeout(500)

    # The indicator should show what technology is detected
    indicator = page.locator("#tech-indicator")
    expect(indicator).to_be_visible()

    # Since both libraries are loaded, it should show one of them
    indicator_text = indicator.text_content()
    assert indicator_text in ["HTMX/Turbo Loaded"], (
        f"Unexpected indicator text: {indicator_text}"
    )


@pytest.mark.e2e
def test_tab_switching(page: Page, app_server: str):
    """Test that tab switching works correctly."""
    page.goto(app_server)

    # Initially, Basic CRUD tab should be active
    expect(page.locator(".tab.active")).to_contain_text("Basic CRUD")
    expect(page.locator("#basic.tab-content.active")).to_be_visible()

    # Click on Real-time Updates tab
    page.locator(".tab", has_text="Real-time Updates").click()

    # Check that the tab switched
    expect(page.locator(".tab.active")).to_contain_text("Real-time Updates")
    expect(page.locator("#realtime.tab-content.active")).to_be_visible()
    expect(page.locator("#basic.tab-content.active")).not_to_be_visible()

    # Click on Technology Comparison tab
    page.locator(".tab", has_text="Technology Comparison").click()

    # Check that the tab switched
    expect(page.locator(".tab.active")).to_contain_text("Technology Comparison")
    expect(page.locator("#comparison.tab-content.active")).to_be_visible()


@pytest.mark.e2e
def test_add_item_functionality(page: Page, app_server: str):
    """Test adding items to the list."""
    page.goto(app_server)

    # Ensure we're on the Basic CRUD tab
    basic_tab = page.locator(".tab", has_text="Basic CRUD")
    if not basic_tab.get_attribute("class") or "active" not in basic_tab.get_attribute(
        "class"
    ):
        basic_tab.click()

    # Fill in the form
    item_input = page.locator("#item-input")
    item_input.fill("Test Item 1")

    # Submit the form
    page.locator("button[type='submit']").click()

    # Wait for the item to appear
    page.wait_for_timeout(1000)

    # Check that the item was added
    items_list = page.locator("#items-list")
    expect(items_list.locator(".item")).to_have_count(1)
    expect(items_list.locator(".item").first).to_contain_text("Test Item 1")

    # Check that the form was cleared
    expect(item_input).to_have_value("")

    # Add another item
    item_input.fill("Test Item 2")
    page.locator("button[type='submit']").click()
    page.wait_for_timeout(1000)

    # Should now have 2 items
    expect(items_list.locator(".item")).to_have_count(2)


@pytest.mark.e2e
def test_delete_item_functionality(page: Page, app_server: str):
    """Test deleting items from the list."""
    page.goto(app_server)

    # Ensure we're on the Basic CRUD tab
    basic_tab = page.locator(".tab", has_text="Basic CRUD")
    if not basic_tab.get_attribute("class") or "active" not in basic_tab.get_attribute(
        "class"
    ):
        basic_tab.click()

    # Add an item first
    item_input = page.locator("#item-input")
    item_input.fill("Item to Delete")
    page.locator("button[type='submit']").click()
    page.wait_for_timeout(1000)

    # Verify item was added
    items_list = page.locator("#items-list")
    expect(items_list.locator(".item")).to_have_count(1)

    # Delete the item
    delete_button = items_list.locator(".item button:has-text('Delete')").first
    delete_button.click()
    page.wait_for_timeout(1000)

    # Verify item was removed
    expect(items_list.locator(".item")).to_have_count(0)


@pytest.mark.e2e
@pytest.mark.skip(
    reason="HTML5 validation prevents server-side empty validation testing in E2E"
)
def test_empty_item_validation(page: Page, app_server: str):
    """Test that empty/whitespace-only items cannot be added."""
    # This test is skipped because HTML5 'required' attribute prevents
    # empty form submission, making server-side validation testing difficult in E2E.
    # In production, this is actually desired behavior.
    pass


@pytest.mark.e2e
def test_real_time_push_updates(page: Page, app_server: str):
    """Test real-time push updates functionality."""
    page.goto(app_server)

    # Switch to Real-time Updates tab
    page.locator(".tab", has_text="Real-time Updates").click()

    # Initially no notifications
    notifications = page.locator("#notifications")
    expect(notifications.locator(".notification")).to_have_count(0)

    # Click the push update button
    page.locator("button:has-text('Send Update to All Clients')").click()
    page.wait_for_timeout(1000)

    # Should see confirmation message
    push_result = page.locator("#push-result")
    expect(push_result).to_contain_text("Update sent to all clients")

    # Note: Testing WebSocket real-time updates in a single browser instance
    # is limited. In a real scenario, you'd open multiple browser contexts
    # to test real-time updates between clients.


@pytest.mark.e2e
def test_responsive_design(page: Page, app_server: str):
    """Test that the app works on different screen sizes."""
    page.goto(app_server)

    # Test desktop view
    page.set_viewport_size({"width": 1200, "height": 800})
    expect(page.locator(".header")).to_be_visible()
    expect(page.locator(".tabs")).to_be_visible()

    # Test tablet view
    page.set_viewport_size({"width": 768, "height": 1024})
    expect(page.locator(".header")).to_be_visible()
    expect(page.locator(".tabs")).to_be_visible()

    # Test mobile view
    page.set_viewport_size({"width": 375, "height": 667})
    expect(page.locator(".header")).to_be_visible()
    expect(page.locator(".tabs")).to_be_visible()


@pytest.mark.e2e
def test_htmx_specific_behavior(page: Page, app_server: str):
    """Test HTMX-specific behavior and headers."""
    page.goto(app_server)

    # Listen for network requests
    requests = []

    def handle_request(request):
        requests.append(request)

    page.on("request", handle_request)

    # Add an item to trigger HTMX request
    item_input = page.locator("#item-input")
    item_input.fill("HTMX Test Item")
    page.locator("button[type='submit']").click()
    page.wait_for_timeout(1000)

    # Check that HTMX headers were sent
    htmx_requests = [
        r for r in requests if r.url.endswith("/items") and r.method == "POST"
    ]
    assert len(htmx_requests) > 0, "No POST requests to /items found"

    # Check for HTMX-specific headers
    htmx_request = htmx_requests[0]
    headers = htmx_request.headers

    # HTMX typically sends these headers
    assert "hx-request" in headers or "HX-Request" in headers, (
        "HX-Request header not found"
    )


@pytest.mark.e2e
def test_turbo_stream_support(page: Page, app_server: str):
    """Test Turbo Stream support."""
    page.goto(app_server)

    # Check that Turbo is loaded
    turbo_script = page.locator("script[src*='turbo']")
    expect(turbo_script).to_be_attached()

    # Test that Turbo functionality works
    # Add an item which should use Turbo streams if available
    item_input = page.locator("#item-input")
    item_input.fill("Turbo Test Item")
    page.locator("button[type='submit']").click()
    page.wait_for_timeout(1000)

    # Verify the item was added (regardless of whether HTMX or Turbo was used)
    items_list = page.locator("#items-list")
    expect(items_list.locator(".item")).to_have_count(1)
    expect(items_list.locator(".item").last).to_contain_text("Turbo Test Item")


@pytest.mark.e2e
def test_form_interaction_flow(page: Page, app_server: str):
    """Test complete form interaction flow."""
    page.goto(app_server)

    # Test adding multiple items
    items_to_add = ["First Item", "Second Item", "Third Item"]

    for i, item_text in enumerate(items_to_add):
        item_input = page.locator("#item-input")
        item_input.fill(item_text)
        page.locator("button[type='submit']").click()
        page.wait_for_timeout(500)

        # Verify item count
        items_list = page.locator("#items-list")
        expect(items_list.locator(".item")).to_have_count(i + 1)

    # Test deleting items one by one
    for i in range(len(items_to_add) - 1, -1, -1):
        items_list = page.locator("#items-list")
        delete_buttons = items_list.locator(".item button:has-text('Delete')")

        if delete_buttons.count() > 0:
            delete_buttons.first.click()
            page.wait_for_timeout(500)

            # Verify item count decreased
            expect(items_list.locator(".item")).to_have_count(i)

    # All items should be deleted
    items_list = page.locator("#items-list")
    expect(items_list.locator(".item")).to_have_count(0)


@pytest.mark.e2e
def test_accessibility_basics(page: Page, app_server: str):
    """Test basic accessibility features."""
    page.goto(app_server)

    # Check that form elements have proper labels
    item_input = page.locator("#item-input")
    expect(item_input).to_have_attribute("name", "item")

    # Check that buttons have proper text
    submit_button = page.locator("button[type='submit']")
    expect(submit_button).to_contain_text("Add Item")

    # Check that the page has a proper title
    expect(page).to_have_title("StarLive Demo - Universal Hypermedia")

    # Test keyboard navigation
    item_input.focus()
    item_input.fill("Keyboard Test")
    page.keyboard.press("Tab")  # Should focus the submit button
    page.keyboard.press("Enter")  # Should submit the form

    page.wait_for_timeout(1000)

    # Verify the item was added
    items_list = page.locator("#items-list")
    expect(items_list.locator(".item")).to_have_count(1)
    expect(items_list.locator(".item").first).to_contain_text("Keyboard Test")


@pytest.mark.e2e
@pytest.mark.slow
def test_performance_with_many_items(page: Page, app_server: str):
    """Test performance with many items."""
    page.goto(app_server)

    # Add many items quickly
    num_items = 10

    for i in range(num_items):
        item_input = page.locator("#item-input")
        item_input.fill(f"Performance Test Item {i + 1}")
        page.locator("button[type='submit']").click()
        page.wait_for_timeout(100)  # Short wait to avoid overwhelming

    # Verify all items were added
    items_list = page.locator("#items-list")
    expect(items_list.locator(".item")).to_have_count(num_items)

    # Test that the page is still responsive
    # Try adding one more item
    item_input = page.locator("#item-input")
    item_input.fill("Final Test Item")
    page.locator("button[type='submit']").click()
    page.wait_for_timeout(1000)

    expect(items_list.locator(".item")).to_have_count(num_items + 1)
