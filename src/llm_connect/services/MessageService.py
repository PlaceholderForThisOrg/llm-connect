from datetime import datetime
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from llm_connect.repositories.MessageRepository import MessageRepository


class MessageService:
    def __init__(self, repo: MessageRepository, session: AsyncSession):
        self.repo = repo
        self.session = session

    async def get_conversation_messages(
        self,
        conversation_id: UUID,
        cursor: datetime | None,
        limit: int,
    ):
        messages, has_next = await self.repo.get_messages_by_cursor(
            conversation_id, cursor, limit
        )

        next_cursor = None
        if messages:
            next_cursor = messages[0].created_at  # oldest in this batch

        return {
            "items": [
                {
                    "id": str(m.id),
                    "role": m.role,
                    "content": m.content,
                    "created_at": m.created_at.isoformat(),
                }
                for m in messages
            ],
            "next_cursor": next_cursor.isoformat() if next_cursor else None,
            "has_next": has_next,
        }
