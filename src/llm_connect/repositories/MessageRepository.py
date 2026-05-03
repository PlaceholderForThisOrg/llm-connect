from datetime import datetime
from typing import Tuple
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from llm_connect.models import Message


class MessageRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_message(
        self,
        conversation_id: UUID,
        role: str,
        content: str,
        meta: dict | None = None,
    ) -> Message:
        message = Message(
            conversation_id=conversation_id,
            role=role,
            content=content,
            meta=meta or {},
        )
        self.session.add(message)
        await self.session.flush()
        return message

    async def get_messages_by_cursor(
        self,
        conversation_id: UUID,
        cursor: datetime | None,
        limit: int = 20,
    ) -> Tuple[list[Message], bool]:
        query = select(Message).where(Message.conversation_id == conversation_id)

        if cursor:
            query = query.where(Message.created_at < cursor)

        # fetch one extra
        query = query.order_by(
            Message.created_at.desc(),
            Message.id.desc(),  # tie-breaker (important)
        ).limit(limit + 1)

        result = await self.session.execute(query)
        messages = list(result.scalars())

        has_next = len(messages) > limit

        # trim to requested limit
        messages = messages[:limit]

        return messages, has_next
