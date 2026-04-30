from typing import Any, Dict
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from llm_connect.models import Conversation
from llm_connect.repositories.ConversationRepository import ConversationRepository
from llm_connect.repositories.MessageRepository import MessageRepository
from llm_connect.services.core.Companion import Companion


class ConversationService:
    def __init__(
        self,
        con_repo: ConversationRepository,
        com: Companion,
        session: AsyncSession,
        message_repo: MessageRepository,
    ):
        self.con_repo = con_repo
        self.com = com
        self.session = session
        self.repo = con_repo
        self.companion = self.com
        self.message_repo = message_repo

    async def stream_chat(
        self,
        conversation_id: UUID,
        user_input: str,
        learner_id: str,
        activity_id: str,
        session_id: str,
        type: str,
    ):
        conversation = await self.con_repo.get_by_id(conversation_id)

        # Save user message
        await self.message_repo.create_message(
            conversation_id=conversation_id,
            role="user",
            content=user_input,
        )

        await self.session.commit()

        # Load history - companion will handle
        # messages = await self.message_repo.get_conversation_messages(conversation_id)

        # companion will also handle
        # openai_messages = [{"role": m.role, "content": m.content} for m in messages]

        # companion
        # 3. Call OpenAI streaming
        # stream = await self.client.chat.completions.create(
        #     model="gpt-4o-mini",
        #     messages=openai_messages,
        #     stream=True,
        # )

        response = ""

        # companion
        # async for chunk in stream:
        #     delta = chunk.choices[0].delta.content or ""
        #     if delta:
        #         full_response += delta
        #         yield delta  # 🔥 streaming happens here

        async for token in self.companion.response_v3(
            learner_id=learner_id,
            conversation_id=conversation_id,
            message=user_input,
            activity_id=activity_id,
            session_id=session_id,
            type=conversation.type,
        ):
            response += token
            yield token

        # Save companion response
        await self.message_repo.create_message(
            conversation_id=conversation_id,
            role="companion",
            content=response,
        )

    async def get_conversations(
        self,
        # db: Session,
        learner_id: str,
        search: str | None,
        page: int,
        page_size: int,
    ) -> Dict[str, Any]:

        offset = (page - 1) * page_size

        conversations, total = await self.repo.get_conversations(
            # db=db,
            learner_id=learner_id,
            search=search,
            limit=page_size,
            offset=offset,
        )

        return {
            "items": [
                {
                    "id": str(conv.id),
                    "title": conv.title,
                    "type": conv.type,
                    "updated_at": conv.updated_ad,
                    "created_ad": conv.created_at,
                }
                for conv in conversations
            ],
            "total": total,
            "page": page,
            "page_size": page_size,
        }

    async def create_conversation(
        self,
        learner_id: str,
        title: str | None,
        type: str | None,
    ) -> Conversation:

        if not learner_id:
            raise ValueError("learner_id is required")

        conversation = await self.repo.create(
            learner_id=learner_id,
            title=title,
            type=type,
        )

        await self.session.commit()
        await self.session.refresh(conversation)

        return conversation

    def create(self):
        pass

    def get_by_id(self, con_id):
        self.con_repo.get_conversation_by_id(con_id)

    def new_con(self, learner_id: str, type: str):
        return self.con_repo.create_new_conversation(type)

    async def sos(self, session_id: str, con_id: str):
        re_content = await self.com.intervene(session_id)

        re_message = {"role": "COMPANION", "content": re_content}

        self.con_repo.add_new_message(
            con_id,
            re_message,
        )

        return re_content

    async def chat(
        self,
        learner_id: str,
        con_id: str,
        message: str,
    ):
        # TODO: Make it stream later

        # [1] Store the message
        message = {
            "role": "LEARNER",
            "content": message,
        }

        self.con_repo.add_new_message(con_id, message)

        re_content = await self.com.response(learner_id, con_id, message)

        re_message = {
            "role": "COMPANION",
            "content": re_content,
        }

        self.con_repo.add_new_message(con_id, re_message)

        return re_message
