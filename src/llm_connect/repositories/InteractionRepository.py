from typing import Dict, List, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from llm_connect.models import Interaction, Progress, Session


class InteractionRepository:
    def __init__(
        self,
        session: AsyncSession,
    ):
        self.session = session
        self.db = session

    async def get_session_history(self, session_id: str) -> List[Dict[str, str]]:
        """
        Return flattened conversation history:
        [
            {"role": "learner", "content": "..."},
            {"role": "npc", "content": "..."}
        ]
        """

        query = (
            select(Session)
            .where(Session.id == session_id)
            .options(
                selectinload(Session.progresses).selectinload(Progress.interactions)
            )
        )

        result = await self.db.execute(query)
        session_obj = result.scalar_one_or_none()

        if not session_obj:
            return []

        history: List[Dict[str, str]] = []

        # Ensure deterministic ordering
        progresses = sorted(session_obj.progresses, key=lambda p: p.created_at)

        for progress in progresses:
            interactions = sorted(progress.interactions, key=lambda i: i.attempt)

            for interaction in interactions:
                # learner input
                if interaction.input:
                    history.append(
                        {
                            "role": "learner",
                            "content": str(interaction.input),
                        }
                    )

                # npc output
                if interaction.output:
                    history.append(
                        {
                            "role": "npc",
                            "content": str(interaction.output),
                        }
                    )

        return history

    async def get_latest_interaction(
        self,
        session_id: UUID,
        progress_id: UUID,
    ) -> Optional[Interaction]:
        stmt = (
            select(Interaction)
            .join(Progress, Interaction.progress_id == Progress.id)
            .where(
                Progress.session_id == session_id,
                Interaction.progress_id == progress_id,
            )
            .order_by(Interaction.created_at.desc())
            .limit(1)
        )

        result = await self.db.execute(stmt)

        return result.scalar_one_or_none()
