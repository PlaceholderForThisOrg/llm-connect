import json

from openai import AsyncOpenAI

from llm_connect import logger
from llm_connect.configs.llm import GPT4OMINI
from llm_connect.services.immerse.PromptBuilder import PromptBuilder


class SessionManager:
    def __init__(self):
        pass
    
    
class RolePlaySessionManager(SessionManager):
    def __init__(self, prompt_builder : PromptBuilder, client : AsyncOpenAI):
        super().__init__()
        self.prompt_builder = prompt_builder
        self.client = client
        
    
    async def can_move(self, session_id : str, content : str, ) -> bool:
        # TODO: Implement whether the learner can move
        # to the next checkpoints
        # [v1]: Only check the task finish
        # [v2]: Aggregate the atomic points completion
        
        prompt = self.prompt_builder.intention_prompt(session_id, content)
        
        response = await self.client.chat.completions.create(
            model=GPT4OMINI, messages=[{"role": "user", "content": prompt}]
        )
        
        
        state = response.choices[0].message.content

        state = json.loads(state)
        state = state["result"]
        # checking the current state is fulfilled or not
        logger.info(f"Should we change state: {state}")
        return state