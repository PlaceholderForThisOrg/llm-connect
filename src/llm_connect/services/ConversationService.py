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

    def create_conversation(
        self,
        learner_id: str,
        title: str | None,
        type: str | None,
    ) -> Conversation:

        if not learner_id:
            raise ValueError("learner_id is required")

        conversation = self.repo.create(
            learner_id=learner_id,
            title=title,
            type=type,
        )

        self.session.commit()
        self.session.refresh(conversation)

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
