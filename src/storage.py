# Storage module
# SQLite database for storing processed emails and analysis results

import aiosqlite
from dataclasses import dataclass
from typing import Optional
import hashlib


@dataclass
class StoredEmail:
    """Email record in database"""
    email_id: str
    from_email: str
    subject: str
    priority: str
    intent: str
    required_action: str
    summary: str
    processed_at: str
    draft_reply: Optional[str] = None


class EmailStorage:
    """SQLite storage for processed emails"""

    def __init__(self, db_path: str = "emails.db"):
        self.db_path = db_path

    async def init_db(self):
        """Create database tables if they don't exist"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS emails (
                    email_id TEXT PRIMARY KEY,
                    from_email TEXT,
                    to_email TEXT,
                    subject TEXT,
                    body TEXT,
                    priority TEXT,
                    intent TEXT,
                    required_action TEXT,
                    summary TEXT,
                    key_points TEXT,
                    draft_reply TEXT,
                    entities TEXT,
                    processed_at TEXT,
                    status TEXT DEFAULT 'processed'
                )
            """)
            await db.execute("""
                CREATE TABLE IF NOT EXISTS processed_hashes (
                    hash TEXT PRIMARY KEY,
                    email_id TEXT,
                    processed_at TEXT
                )
            """)
            await db.commit()

    def generate_email_id(self, email_data) -> str:
        """Generate unique ID from email content"""
        content = f"{email_data.from_email}{email_data.subject}{email_data.body[:100]}"
        return hashlib.md5(content.encode()).hexdigest()[:16]

    async def is_processed(self, email_data) -> bool:
        """Check if this email was already processed (idempotent)"""
        email_id = self.generate_email_id(email_data)
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                "SELECT 1 FROM processed_hashes WHERE hash = ?",
                (email_id,)
            )
            row = await cursor.fetchone()
            return row is not None

    async def save_email(self, email_data, analysis, processed_at: str):
        """Save processed email to database"""
        email_id = self.generate_email_id(email_data)

        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                INSERT OR REPLACE INTO emails (
                    email_id, from_email, to_email, subject, body,
                    priority, intent, required_action, summary,
                    key_points, draft_reply, entities, processed_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                email_id,
                email_data.from_email,
                email_data.to_email,
                email_data.subject,
                email_data.body,
                analysis.priority,
                analysis.intent,
                analysis.required_action,
                analysis.summary,
                str(analysis.key_points),
                analysis.suggested_reply,
                str(analysis.entities),
                processed_at
            ))

            await db.execute("""
                INSERT OR REPLACE INTO processed_hashes (hash, email_id, processed_at)
                VALUES (?, ?, ?)
            """, (email_id, email_id, processed_at))

            await db.commit()

    async def get_recent_emails(self, limit: int = 10):
        """Get most recently processed emails"""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("""
                SELECT email_id, from_email, subject, priority, intent,
                       required_action, summary, processed_at
                FROM emails
                ORDER BY processed_at DESC
                LIMIT ?
            """, (limit,))
            rows = await cursor.fetchall()
            return [dict(zip(["id", "from", "subject", "priority", "intent",
                            "action", "summary", "date"], row)) for row in rows]
