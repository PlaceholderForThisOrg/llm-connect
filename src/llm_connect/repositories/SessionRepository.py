import json
import uuid
from datetime import datetime, timezone
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from llm_connect.models import Progress, Session
from llm_connect.proto.session.sessions_v3 import sessions_v3


class SessionRepository:
    def __init__(
        self,
        session: AsyncSession,
    ):
        self.file_path = (
            Path(__file__).resolve().parent.parent
            / "proto"
            / "runtime_db"
            / "sessions_v3.json"
        )

        self.session = session
        self.db = session

        # Ensure directory exists
        self.file_path.parent.mkdir(parents=True, exist_ok=True)

        # Load existing session if exists
        if self.file_path.exists():
            try:
                with open(self.file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    sessions_v3.update(data)
            except Exception:
                # Ignore for prototype (corrupt or empty file)
                pass

        # Initial sync (ensures file exists)
        self.sync()

    async def get_with_progress(self, session_id):
        stmt = (
            select(Session)
            .where(Session.id == session_id)
            .options(
                selectinload(Session.progresses).selectinload(Progress.interactions)
            )
        )

        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def create(self, session: Session) -> Session:
        self.db.add(session)
        await self.db.commit()
        await self.db.refresh(session)
        return session

    async def get(self, session_id):
        return await self.db.get(Session, session_id)

    def sync(self):
        """Persist session to disk"""
        try:
            with open(self.file_path, "w", encoding="utf-8") as f:
                json.dump(sessions_v3, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"[session sync error] {e}")

    def get_session_by_id(self, session_id: str):
        # Prototype: single session
        return sessions_v3[session_id]

    def get_current_checkpoint(self, session_id: str):
        session = sessions_v3[session_id]
        return session.get("current_goal")

    def update_next_checkpoint(self, session_id, checkpoint_id: str):
        session = sessions_v3[session_id]
        session["current_goal"] = checkpoint_id
        self.sync()

    def add_interaction(self, session_id, interaction):

        session = sessions_v3[session_id]
        if "history" not in session:
            session["history"] = []

        session["history"].append(interaction)
        self.sync()

    def increase_retries(self, session_id: str, goal_id: str):
        session = sessions_v3[session_id]
        retries = session["retries"]

        if goal_id not in retries:
            retries[goal_id] = 0

        retries[goal_id] += 1

        self.sync()

    def create_session(self, activity_id, con_id):
        # Generate unique session ID
        session_id = str(uuid.uuid4())

        # Create new session structure
        new_session = {
            "session_id": session_id,
            "activity_id": activity_id,
            "con_id": con_id,
            "current_goal": "0",
            "history": [],
            "time_start": datetime.now(timezone.utc).timestamp(),
            "status": "RUNNING",
            "retries": {},
        }

        # Store in global dict
        sessions_v3[session_id] = new_session

        # Persist to disk
        self.sync()

        return new_session
