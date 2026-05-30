import sqlite3
from uuid import uuid4

import requests
from playwright.sync_api import Page


def test_history_sidebar_shows_runs(page: Page, live_server_url: str):
    api = f"{live_server_url}/api"
    for i in range(3):
        res = requests.post(
            f"{api}/pipelines",
            json={
                "project_name": f"History Project {i}",
                "description": "Test history",
                "provider": "ollama",
                "model": "llama3.2",
            },
        )
        assert res.status_code == 201
        pid = res.json()["pipeline"]["id"]
        requests.delete(f"{api}/pipelines/{pid}")

    page.goto(f"{live_server_url}/")
    page.evaluate("localStorage.setItem('hasSeenTutorial', 'true')")
    page.reload()
    page.wait_for_selector("text=Select AI Model", state="visible", timeout=10000)

    page.click("text=History")
    page.wait_for_selector("text=Project History", state="visible")


def test_delete_confirmation_dialog(page: Page, live_server):
    url = live_server["url"]
    tmpdir = live_server["tmpdir"]
    api = f"{url}/api"

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
            pid, "Delete Me", "Test delete", "ollama", "llama3.2",
            "completed", None, 100,
            "2024-01-01T00:00:00", "2024-01-01T00:00:00", "2024-01-01T00:00:00",
            None, None,
        ),
    )
    conn.commit()
    conn.close()

    page.goto(url)
    page.evaluate("localStorage.setItem('hasSeenTutorial', 'true')")
    page.reload()
    page.wait_for_selector("text=Delete Me", state="visible", timeout=10000)

    page.click("text=History")
    page.wait_for_selector("text=Project History", state="visible")
    page.wait_for_selector("text=Delete Me", state="visible")
    page.on("dialog", lambda dialog: dialog.accept())
    page.click("button:has-text('Delete')")

    res2 = requests.get(f"{api}/pipelines/{pid}")
    assert res2.status_code == 404
