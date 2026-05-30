import sqlite3
from uuid import uuid4

from playwright.sync_api import Page


def test_checkpoint_modal_appears_and_approves(page: Page, live_server):
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
            pid, "Checkpoint Test", "Test checkpoint modal", "ollama", "llama3.2",
            "checkpoint", "req_engineer", 12,
            "2024-01-01T00:00:00", "2024-01-01T00:00:00", None,
            "requirements.md", None,
        ),
    )
    conn.commit()
    conn.close()

    page.goto(url)
    page.evaluate("localStorage.setItem('hasSeenTutorial', 'true')")
    page.reload()
    page.wait_for_selector("text=Checkpoint Test", state="visible", timeout=10000)
    page.wait_for_selector("[aria-label='Checkpoint approval']", state="visible")
    page.wait_for_selector("button:has-text('Approve & Continue')", state="visible")
    page.wait_for_selector("button:has-text('Request Changes')", state="visible")

    page.click("button:has-text('Request Changes')")
    page.wait_for_selector("textarea[aria-label='Feedback text']", state="visible")

    page.click("text=Cancel")
    page.wait_for_selector("[aria-label='Checkpoint approval']", state="hidden")
