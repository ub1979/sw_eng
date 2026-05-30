import os
import sqlite3
from uuid import uuid4

from playwright.sync_api import Page


def test_artifact_browser_shows_files(page: Page, live_server):
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
            pid, "Artifact Test", "Test artifacts", "ollama", "llama3.2",
            "completed", None, 100,
            "2024-01-01T00:00:00", "2024-01-01T00:00:00", "2024-01-01T00:00:00",
            None, None,
        ),
    )
    conn.commit()
    conn.close()

    project_dir = f"{tmpdir}/projects/{pid}"
    os.makedirs(project_dir, exist_ok=True)
    with open(f"{project_dir}/README.md", "w") as f:
        f.write("# Test Project\n\nHello world.")
    with open(f"{project_dir}/main.py", "w") as f:
        f.write("print('hello')")

    page.goto(url)
    page.evaluate("localStorage.setItem('hasSeenTutorial', 'true')")
    page.reload()
    page.wait_for_selector("text=Artifact Test", state="visible", timeout=10000)
    page.wait_for_selector("button:has-text('Browse Artifacts')", state="visible")
    page.click("text=Browse Artifacts")
    page.wait_for_selector("text=README.md", state="visible")
    page.wait_for_selector("text=main.py", state="visible")

    page.click("text=README.md")
    page.wait_for_selector("text=Artifact Preview", state="visible")
    page.wait_for_selector("text=Test Project", state="visible")
