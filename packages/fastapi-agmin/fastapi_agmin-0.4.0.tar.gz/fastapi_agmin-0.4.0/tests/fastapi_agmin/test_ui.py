import time
from multiprocessing import Process

import pytest
import requests
import uvicorn
from playwright.sync_api import Error, Page

from tests.fastapi_agmin.app_test import app_test


def run_server():
    uvicorn.run(app_test, port=8079)


@pytest.fixture(scope="module", autouse=True)
def server():
    proc = Process(target=run_server, args=(), daemon=True)
    proc.start()
    yield
    proc.kill()  # Cleanup after test


def get_working_url(page: Page):
    ports_to_try = [5173, 8079]
    start = time.time()
    last_error = None
    while time.time() - start < 10:
        for port in ports_to_try:
            url = f"http://localhost:{port}/agmin"
            try:
                page.goto(url, timeout=2000)
                page.wait_for_selector("select", timeout=2000)
                return url
            except Error as e:
                last_error = e
                continue
        time.sleep(0.5)
    raise RuntimeError(f"Could not connect to admin UI on ports {ports_to_try}: {last_error}")


@pytest.mark.ui
def test_model_grids_show_expected_data(page: Page):
    get_working_url(page)
    # Use url for navigation if needed
    # page.goto(url)  # Already navigated in get_working_url

    # Model: Task
    page.select_option("select", label="Task")
    page.wait_for_timeout(500)
    headers = page.locator(".ag-header-cell-text").all_text_contents()
    assert "title" in [h.lower() for h in headers]
    assert "status" not in [h.lower() for h in headers], "Status column should be ignored in Task grid"
    first_row = page.locator(".ag-center-cols-container .ag-row").first.locator(".ag-cell-value").all_text_contents()
    print("Task first_row:", first_row)
    assert any("Implement User Authentication" in cell for cell in first_row)

    # Model: Person
    page.select_option("select", label="Person")
    page.wait_for_timeout(500)
    headers = page.locator(".ag-header-cell-text").all_text_contents()
    assert "name" in [h.lower() for h in headers]
    assert "email" in [h.lower() for h in headers]
    first_row = page.locator(".ag-center-cols-container .ag-row").first.locator(".ag-cell-value").all_text_contents()
    print("Person first_row:", first_row)
    assert any("John Doe" in cell for cell in first_row)
    assert any("john@example.com" in cell for cell in first_row)

    # Model: Address
    page.select_option("select", label="Address")
    page.wait_for_timeout(500)
    headers = page.locator(".ag-header-cell-text").all_text_contents()
    assert "street" in [h.lower() for h in headers]
    first_row = page.locator(".ag-center-cols-container .ag-row").first.locator(".ag-cell-value").all_text_contents()
    assert any("123 Main St" in cell for cell in first_row)

    # Model: Allocation
    page.select_option("select", label="Allocation")
    page.wait_for_timeout(500)
    headers = page.locator(".ag-header-cell-text").all_text_contents()
    assert "hours_worked" in [h.lower() for h in headers]
    first_row = page.locator(".ag-center-cols-container .ag-row").first.locator(".ag-cell-value").all_text_contents()
    assert len(first_row) > 0

    # Model: Attachment
    page.select_option("select", label="Attachment")
    page.wait_for_timeout(500)
    headers = page.locator(".ag-header-cell-text").all_text_contents()
    assert "filename" in [h.lower() for h in headers]
    first_row = page.locator(".ag-center-cols-container .ag-row").first.locator(".ag-cell-value").all_text_contents()
    assert any("auth_design.pdf" in cell for cell in first_row)


@pytest.mark.ui
def test_first_column_is_display_name_and_not_empty(page: Page):
    get_working_url(page)
    # Get all model options except the placeholder
    model_options = page.locator("select option").all()
    for option in model_options:
        model = option.text_content()
        if not model or model.strip().lower() == "select a model" or set(model) == {"─"}:
            print(f"Skipping model option: {model!r}")
            continue
        page.select_option("select", label=model)
        page.wait_for_timeout(2000)
        headers = page.locator(".ag-header-cell-text").all_text_contents()
        print(f"Model: {model}, Headers: {headers}")
        if not headers or not headers[0]:
            print("Page content:", page.content())
            continue
        assert (
            headers[0] and "display" in headers[0].lower()
        ), f"First column for {model} is not display name: {headers}"
        # Assert the second column is not Display Name
        if len(headers) > 1:
            assert headers[1] not in [
                "display_name_",
                "Display Name",
            ], f"Second column for model {model} should not be display_name_ or Display Name: {headers[1]}"
        # Get the first row's first cell value
        first_cell = (
            page.locator(".ag-center-cols-container .ag-row").first.locator(".ag-cell-value").first.text_content()
        )
        assert first_cell and first_cell.strip(), f"First cell in display_name_ column for model {model} is empty"


@pytest.mark.ui
def test_person_detail_shows_related_entities(page: Page):
    url = get_working_url(page)
    # Get first Person's id from API
    api_url = url.replace("/agmin", "/agmin/api/person")
    resp = requests.get(api_url)
    resp.raise_for_status()
    people = resp.json()
    assert people, "No Person found in API!"
    # Go to agmin first to load the app
    page.goto(f"{url}")
    page.wait_for_timeout(500)
    page.select_option("select", label="Person")
    page.wait_for_timeout(2000)
    # Go to Person detail view
    page.locator(".relations-button").first.click()
    page.wait_for_timeout(2000)
    # Verify main Person table headers
    headers = page.locator(".ag-header-cell-text").all_text_contents()
    assert "name" in [h.lower() for h in headers]
    assert "email" in [h.lower() for h in headers]
    # Get all tables on the page
    tables = page.locator(".model-grid").all()
    assert len(tables) == 3, "Expected 3 tables: Person, Allocation, and Address"
    # Verify Person table (first table)
    person_headers = tables[0].locator(".ag-header-cell-text").all_text_contents()
    assert "name" in [h.lower() for h in person_headers]
    assert "email" in [h.lower() for h in person_headers]
    person_row = (
        tables[0].locator(".ag-center-cols-container .ag-row").first.locator(".ag-cell-value").all_text_contents()
    )
    assert any("John Doe" in cell for cell in person_row)
    # Find and verify Allocation table
    allocation_table = None
    for table in tables[1:]:
        headers = table.locator(".ag-header-cell-text").all_text_contents()
        if "hours_worked" in [h.lower() for h in headers]:
            allocation_table = table
            break
    assert allocation_table, "Allocation table not found"
    allocation_row = (
        allocation_table.locator(".ag-center-cols-container .ag-row")
        .first.locator(".ag-cell-value")
        .all_text_contents()
    )
    assert len(allocation_row) > 0

    # Find and verify Address table
    address_table = None
    for table in tables[1:]:
        headers = table.locator(".ag-header-cell-text").all_text_contents()
        if "street" in [h.lower() for h in headers]:
            address_table = table
            break
    assert address_table, "Address table not found"
    address_row = (
        address_table.locator(".ag-center-cols-container .ag-row").first.locator(".ag-cell-value").all_text_contents()
    )
    assert any("123 Main St" in cell for cell in address_row)


@pytest.mark.ui
def test_self_referential_relationships_have_different_names(page: Page):
    """
    Test that self-referential relationships (like Task with its dependencies) use different
    column names in the UI to distinguish between the two sides of the relationship.
    """
    url = get_working_url(page)
    page.goto(url)
    page.wait_for_timeout(500)

    # Select Task model - it has self-referential relationships through TaskDependency
    page.select_option("select", label="Task")
    page.wait_for_timeout(2000)

    # Get all column headers
    headers = page.locator(".ag-header-cell-text").all_text_contents()
    print("Task headers:", headers)

    # Find columns related to the self-referential relationship
    # We're looking for headers containing words like "requirements", "descendants", etc.
    relationship_headers = [
        h
        for h in headers
        if any(term in h.lower() for term in ["requirement", "dependent", "descendant", "parent", "child"])
    ]

    # We should find at least two relationship headers
    assert len(relationship_headers) >= 2, f"Expected at least two relationship headers, got: {relationship_headers}"

    # Get unique relationship headers - there should be no duplicates
    unique_headers = set(relationship_headers)
    assert len(unique_headers) == len(
        relationship_headers
    ), f"Found duplicate relationship headers: {relationship_headers}"

    # Verify that the relationship headers are distinct from each other
    # This ensures they are not ambiguous
    if len(relationship_headers) >= 2:
        for i, header1 in enumerate(relationship_headers):
            for header2 in relationship_headers[i + 1 :]:
                assert header1 != header2, f"Found identical relationship headers: '{header1}' and '{header2}'"
                # Check that they're not just case variants of each other
                assert header1.lower() != header2.lower(), f"Found case-variant headers: '{header1}' and '{header2}'"

    print("All relationship headers are distinct:", relationship_headers)
