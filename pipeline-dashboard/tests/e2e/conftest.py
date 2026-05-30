import os
import socket
import sqlite3
import subprocess
import tempfile
import time

import pytest
import requests


def _find_free_port():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


@pytest.fixture(scope="session")
def live_server():
    tmpdir = tempfile.mkdtemp()
    projects_dir = os.path.join(tmpdir, "projects")
    os.makedirs(projects_dir, exist_ok=True)

    env = os.environ.copy()
    env["PIPELINE_DB_PATH"] = os.path.join(tmpdir, "pipeline.db")
    env["PIPELINE_PROJECTS_DIR"] = projects_dir

    port = _find_free_port()
    url = f"http://127.0.0.1:{port}"

    proc = subprocess.Popen(
        ["python", "-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", str(port)],
        cwd="/Users/u/funcoding/skills/pipeline-dashboard",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=env,
    )
    for _ in range(30):
        try:
            import urllib.request
            with urllib.request.urlopen(url + "/api/health", timeout=1):
                break
        except Exception:
            time.sleep(0.5)
    else:
        stderr = proc.stderr.read1(4096).decode("utf-8", errors="replace") if proc.stderr else ""
        proc.terminate()
        raise RuntimeError(f"Server did not start. stderr: {stderr}")
    yield {"url": url, "tmpdir": tmpdir}
    proc.terminate()
    try:
        proc.wait(timeout=5)
    except subprocess.TimeoutExpired:
        proc.kill()


@pytest.fixture
def live_server_url(live_server):
    return live_server["url"]


@pytest.fixture(autouse=True)
def cleanup_pipelines(live_server):
    url = live_server["url"]
    tmpdir = live_server["tmpdir"]
    db_path = os.path.join(tmpdir, "pipeline.db")
    if os.path.exists(db_path):
        conn = sqlite3.connect(db_path)
        try:
            conn.execute("PRAGMA foreign_keys = OFF")
            conn.execute("DELETE FROM security_events")
            conn.execute("DELETE FROM agent_runs")
            conn.execute("DELETE FROM pipeline_runs")
            conn.execute("PRAGMA foreign_keys = ON")
            conn.commit()
        except (sqlite3.OperationalError, sqlite3.IntegrityError):
            pass
        conn.close()
    yield
