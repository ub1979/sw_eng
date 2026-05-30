import pytest
import sqlite3
from uuid import uuid4

from playwright.sync_api import Page


def test_start_pipeline_shows_agent_cards(page: Page, live_server_url: str):
    page.goto(live_server_url)
    page.evaluate("localStorage.setItem('hasSeenTutorial', 'true')")
    page.reload()
    page.wait_for_selector("text=Select AI Model", state="visible", timeout=10000)

    page.fill("textarea[aria-label='Project description']", "A simple portfolio website")
    page.click("button:has-text('Start Pipeline')")
    page.wait_for_selector("text=A simple portfolio website", state="visible", timeout=10000)
    page.wait_for_selector("text=Agent Pipeline", state="visible")
    page.wait_for_selector("[role='progressbar']", state="visible")


def test_provider_model_dropdown_loads(page: Page, live_server_url: str):
    # Intercept providers API to simulate Ollama with models
    page.route(f"{live_server_url}/api/providers", lambda route: route.fulfill(
        status=200,
        content_type="application/json",
        body='[{"name":"ollama","available":true,"models":["llama3.2","mistral"],"error":null},{"name":"claude","available":true,"models":["claude"],"error":null},{"name":"gemini","available":false,"models":[],"error":"Gemini CLI is not running in a trusted directory. Use --skip-trust."}]',
    ))
    page.goto(live_server_url)
    page.evaluate("localStorage.setItem('hasSeenTutorial', 'true')")
    page.reload()
    page.wait_for_selector("text=Select AI Model", state="visible", timeout=10000)

    # Trigger provider health check by focusing the select
    page.focus("select[aria-label='Model provider']")
    page.wait_for_timeout(600)

    # Model dropdown should populate with Ollama models
    model_select = page.locator("select[aria-label='Model']")
    options = model_select.locator("option").count()
    assert options > 1, f"Model dropdown should have options, got {options}"


def test_provider_error_surfaces_in_ui(page: Page, live_server_url: str):
    # Intercept providers API to simulate Gemini as unavailable with actionable error
    page.route(f"{live_server_url}/api/providers", lambda route: route.fulfill(
        status=200,
        content_type="application/json",
        body='[{"name":"ollama","available":true,"models":["llama3.2"],"error":null},{"name":"claude","available":true,"models":["claude"],"error":null},{"name":"gemini","available":false,"models":[],"error":"Gemini CLI is not running in a trusted directory. To proceed, use --skip-trust."}]',
    ))
    page.goto(live_server_url)
    page.evaluate("localStorage.setItem('hasSeenTutorial', 'true')")
    page.reload()
    page.wait_for_selector("text=Select AI Model", state="visible", timeout=10000)

    # Select Gemini via JS to ensure Alpine dispatches the change
    page.evaluate("""
        const select = document.querySelector("select[aria-label='Model provider']");
        select.value = 'gemini';
        select.dispatchEvent(new Event('input', { bubbles: true }));
        select.dispatchEvent(new Event('change', { bubbles: true }));
    """)

    # Wait for error to appear
    error_msg = page.locator(".ds-inline-error")
    error_msg.wait_for(state="visible", timeout=5000)
    text = error_msg.text_content()
    assert text and "--skip-trust" in text, f"Expected actionable error with --skip-trust hint, got: {text}"


def test_pipeline_progress_updates(page: Page, live_server):
    url = live_server["url"]
    tmpdir = live_server["tmpdir"]

    pid = str(uuid4())
    db_path = f"{tmpdir}/pipeline.db"
    conn = sqlite3.connect(db_path)
    conn.execute(
        """
        INSERT INTO pipeline_runs
        (id, project_name, description, provider, model, status, current_agent,
         overall_progress, created_at, updated_at, completed_at,
         checkpoint_artifact_path, checkpoint_feedback)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            pid, "Progress Test", "Test progress", "ollama", "llama3.2",
            "running", "sw_architect", 25,
            "2024-01-01T00:00:00", "2024-01-01T00:00:00", None,
            None, None,
        ),
    )
    conn.commit()
    conn.close()

    page.goto(url)
    page.evaluate("localStorage.setItem('hasSeenTutorial', 'true')")
    page.reload()
    page.wait_for_selector("text=Progress Test", state="visible", timeout=10000)
    progress = page.locator("[role='progressbar']")
    assert progress.get_attribute("aria-valuenow") == "25"
