from typing import Any, Dict

from sqlalchemy.ext.asyncio import AsyncSession

from llm_connect.models import Conversation
from llm_connect.repositories.ConversationRepository import ConversationRepository
from llm_connect.services.core.Companion import Companion


class ConversationService:
    def __init__(
        self,
        con_repo: ConversationRepository,
        com: Companion,
        session: AsyncSession,
    ):
        self.con_repo = con_repo
        self.com = com
        self.session = session
        self.repo = con_repo

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
