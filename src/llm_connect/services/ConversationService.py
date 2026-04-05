from llm_connect.repositories.ConversationRepository import ConversationRepository
from llm_connect.services.core.Companion import Companion


class ConversationService:
    def __init__(
        self,
        con_repo: ConversationRepository,
        com: Companion,
    ):
        self.con_repo = con_repo
        self.com = com

    def create(self):
        pass

    def get_by_id(self, con_id):
        self.con_repo.get_conversation_by_id(con_id)

    async def chat(
        self,
        learner_id: str,
        con_id: str,
        message: str,
    ):
        # TODO: Make it stream later

        # [1] Store the message
        message = {"role": "LEARNER", "content": message}

        self.con_repo.add_new_message(con_id, message)

        re_content = await self.com.response(learner_id, con_id, message)

        re_message = {"role": "COMPANION", "content": re_content}

        self.con_repo.add_new_message(con_id, re_message)

        return re_message
