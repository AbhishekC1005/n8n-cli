import aiosqlite
from datetime import datetime
from typing import Optional

from config import settings, ensure_agent_home


db_path = settings.AGENT_HOME / "n8n_agent.db"


async def init_db():
    ensure_agent_home()
    async with aiosqlite.connect(db_path) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS workflow_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                workflow_id TEXT NOT NULL,
                workflow_name TEXT NOT NULL,
                action TEXT NOT NULL,
                prompt_used TEXT NOT NULL,
                session_id TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS session_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL UNIQUE,
                started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                ended_at TIMESTAMP,
                turns_count INTEGER DEFAULT 0,
                workflows_touched INTEGER DEFAULT 0
            )
        """)
        await db.commit()


async def log_workflow(
    workflow_id: str,
    workflow_name: str,
    action: str,
    prompt_used: str,
    session_id: str,
):
    async with aiosqlite.connect(db_path) as db:
        await db.execute(
            """INSERT INTO workflow_log 
               (workflow_id, workflow_name, action, prompt_used, session_id, created_at)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (
                workflow_id,
                workflow_name,
                action,
                prompt_used,
                session_id,
                datetime.utcnow().isoformat(),
            ),
        )
        await db.commit()


async def get_session_history(session_id: str, limit: int = 50):
    async with aiosqlite.connect(db_path) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            """SELECT * FROM workflow_log 
               WHERE session_id = ? 
               ORDER BY created_at DESC 
               LIMIT ?""",
            (session_id, limit),
        ) as cursor:
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]
