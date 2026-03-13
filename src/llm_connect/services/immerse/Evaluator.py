import json
from xmlrpc.client import boolean

from openai import AsyncOpenAI

from llm_connect import logger
from llm_connect.configs.llm import GPT4OMINI
from llm_connect.services.immerse import PromptBuilder


class Evaluator:
    def __init__(self, client: AsyncOpenAI, prompt_builder: PromptBuilder):
        self.client = client
        self.prompt_builder = prompt_builder

    async def next_state(self, input: str) -> boolean:
        # [1] Build the prompt

        prompt = self.prompt_builder.intention_prompt(1, input)

        response = await self.client.chat.completions.create(
            model=GPT4OMINI, messages=[{"role": "user", "content": prompt}]
        )

        state = response.choices[0].message.content

        state = json.loads(state)
        state = state["result"]
        # checking the current state is fulfilled or not
        logger.info(f"Should we change state: {state}")
        return state
