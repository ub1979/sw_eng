import os
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from pathlib import Path

import aiosqlite

from app.config import settings

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS pipeline_runs (
    id TEXT PRIMARY KEY,
    project_name TEXT NOT NULL,
    description TEXT NOT NULL,
    provider TEXT NOT NULL,
    model TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'idle',
    current_agent TEXT,
    overall_progress INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    completed_at TEXT,
    checkpoint_artifact_path TEXT,
    checkpoint_feedback TEXT,
    fast_model TEXT,
    build_profile TEXT
);

CREATE TABLE IF NOT EXISTS agent_runs (
    id TEXT PRIMARY KEY,
    pipeline_id TEXT NOT NULL REFERENCES pipeline_runs(id),
    agent_name TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending',
    started_at TEXT,
    completed_at TEXT,
    duration_ms INTEGER,
    artifact_paths TEXT NOT NULL DEFAULT '[]',
    error_message TEXT,
    log_tail TEXT
);

CREATE TABLE IF NOT EXISTS security_events (
    id TEXT PRIMARY KEY,
    pipeline_id TEXT REFERENCES pipeline_runs(id),
    timestamp TEXT NOT NULL,
    event_type TEXT NOT NULL,
    detail TEXT NOT NULL,
    command TEXT
);

CREATE INDEX IF NOT EXISTS idx_agent_runs_pipeline ON agent_runs(pipeline_id);
CREATE INDEX IF NOT EXISTS idx_security_events_pipeline ON security_events(pipeline_id);
CREATE INDEX IF NOT EXISTS idx_pipeline_runs_status ON pipeline_runs(status);
"""


async def get_db_path() -> str:
    db_path = os.environ.get("PIPELINE_DB_PATH") or str(settings.data_dir / "pipeline.db")
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    return db_path


async def init_schema(conn: aiosqlite.Connection) -> None:
    await conn.executescript(SCHEMA_SQL)
    await _migrate_columns(conn)
    await conn.commit()


async def _migrate_columns(conn: aiosqlite.Connection) -> None:
    """Idempotently add columns introduced after the original schema, so existing
    databases pick them up without a manual migration."""
    cursor = await conn.execute("PRAGMA table_info(pipeline_runs)")
    existing = {row[1] for row in await cursor.fetchall()}
    for column, ddl in (
        ("fast_model", "ALTER TABLE pipeline_runs ADD COLUMN fast_model TEXT"),
        ("build_profile", "ALTER TABLE pipeline_runs ADD COLUMN build_profile TEXT"),
    ):
        if column not in existing:
            await conn.execute(ddl)


@asynccontextmanager
async def get_db():
    db_path = await get_db_path()
    async with aiosqlite.connect(db_path) as conn:
        await conn.execute("PRAGMA foreign_keys=ON")
        conn.row_factory = aiosqlite.Row
        yield conn


async def backup_database() -> None:
    db_path = await get_db_path()
    db_file = Path(db_path)
    if not db_file.exists():
        return
    backup_dir = db_file.parent / "backups"
    backup_dir.mkdir(parents=True, exist_ok=True)
    existing = sorted(backup_dir.glob("pipeline_*.db"))
    if existing:
        latest = existing[-1]
        if latest.stat().st_size == db_file.stat().st_size and latest.stat().st_mtime >= db_file.stat().st_mtime - 300:
            return
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    backup_path = backup_dir / f"pipeline_{timestamp}.db"
    import shutil
    shutil.copy2(db_path, backup_path)
    while len(list(backup_dir.glob("pipeline_*.db"))) > 20:
        oldest = sorted(backup_dir.glob("pipeline_*.db"))[0]
        oldest.unlink()


async def init_database() -> None:
    db_path = await get_db_path()
    async with aiosqlite.connect(db_path) as conn:
        await conn.execute("PRAGMA journal_mode=WAL")
        await conn.execute("PRAGMA foreign_keys=ON")
        await init_schema(conn)
