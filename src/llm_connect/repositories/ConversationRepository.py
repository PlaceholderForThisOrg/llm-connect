import json
import os
import uuid
from typing import List, Tuple

from sqlalchemy import desc, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from llm_connect.models import Conversation, Message
from llm_connect.proto.conversations_v1 import conversations_v1


class ConversationRepository:
    def __init__(self, session: AsyncSession):

        self.session = session

        self.file_path = os.path.abspath(
            os.path.join(
                os.path.dirname(__file__), "../proto/runtime_db/conversations.json"
            )
        )

        # Ensure directory exists
        os.makedirs(os.path.dirname(self.file_path), exist_ok=True)

        # Load existing data if file exists
        if os.path.exists(self.file_path):
            try:
                with open(self.file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    conversations_v1.update(data)
            except Exception:
                # If file is corrupted or empty, ignore for prototype
                pass

        # Initial sync to ensure file exists
        self.sync()

    async def get_by_id(self, id):
        stmt = select(Conversation).where(Conversation.id == id)

        result = await self.session.execute(stmt)

        return result.scalar()

    async def get_conversations(
        self,
        learner_id: str,
        search: str | None,
        limit: int,
        offset: int,
    ) -> Tuple[List[Conversation], int]:

        base_query = select(Conversation).where(Conversation.learner_id == learner_id)

        if search:
            base_query = base_query.join(Message, isouter=True).where(
                or_(
                    Conversation.title.ilike(f"%{search}%"),
                    Message.content.ilike(f"%{search}%"),
                )
            )

        count_query = select(func.count(func.distinct(Conversation.id))).select_from(
            Conversation
        )

        if search:
            count_query = count_query.join(Message, isouter=True).where(
                or_(
                    Conversation.title.ilike(f"%{search}%"),
                    Message.content.ilike(f"%{search}%"),
                )
            )

        count_query = count_query.where(Conversation.learner_id == learner_id)

        count_result = await self.session.execute(count_query)
        total = count_result.scalar_one()

        data_query = (
            base_query.order_by(desc(Conversation.updated_ad))
            .limit(limit)
            .offset(offset)
        )

        result = await self.session.execute(data_query)

        conversations = result.scalars().unique().all()

        return conversations, total

    async def create(
        self,
        learner_id: str,
        title: str | None,
        type: str | None,
    ) -> Conversation:

        conversation = Conversation(
            learner_id=learner_id,
            title=title,
            type=type,
        )

        self.session.add(conversation)
        await self.session.flush()
        return conversation

    def sync(self):
        """Write current conversations to file"""
        try:
            with open(self.file_path, "w", encoding="utf-8") as f:
                json.dump(conversations_v1, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"[sync error] {e}")

    def create_new_conversation(self, type: str):
        """Create a new conversation and persist it"""
        con_id = str(uuid.uuid4())

        conversations_v1[con_id] = {
            "id": con_id,
            "type": type,
            "messages": [],
        }

        self.sync()
        return con_id

    def get_conversation_by_id(self, con_id):
        return conversations_v1.get(con_id)

    def add_new_message(self, con_id, message):
        conversations_v1[con_id]["messages"].append(message)
        self.sync()
