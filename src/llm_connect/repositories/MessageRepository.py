from datetime import datetime
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

    async def get_conversation_messages(
        self,
        conversation_id: UUID,
    ) -> list[Message]:

        # FIXME: enable cursor pagination

        result = await self.session.execute(
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at.asc())
        )
        return list(result.scalars())

    async def get_messages_by_cursor(
        self,
        conversation_id: UUID,
        cursor: datetime | None,
        limit: int = 20,
    ) -> list[Message]:
        query = select(Message).where(Message.conversation_id == conversation_id)

        if cursor:
            query = query.where(Message.created_at < cursor)

        query = query.order_by(Message.created_at.desc()).limit(limit)

        result = await self.session.execute(query)
        messages = list(result.scalars())

        # reverse to chronological order for UI
        return list(reversed(messages))
