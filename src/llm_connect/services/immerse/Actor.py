from openai import AsyncOpenAI

from llm_connect.configs.llm import GPT41
from llm_connect.proto import scenario
from llm_connect.services.immerse import PromptBuilder


class Actor:
    def __init__(self, client: AsyncOpenAI, prompt_builder: PromptBuilder):
        self.client = client
        self.prompt_builder = prompt_builder

    async def say(self, input: str):
        # [1] Building the prompt for the actor
        prompt = self.prompt_builder.actor_prompt(1, input)

        # [1.1] For accumuate the tokens
        response = ""

        # [2] Use that for the actor LLM and then stream the tokens back
        async with self.client.chat.completions.stream(
            model=GPT41, messages=[{"role": "user", "content": prompt}]
        ) as stream_manager:
            async for event in stream_manager:
                if event.type == "content.delta":
                    response += event.delta
                    yield event.delta

                if event.type == "content.done":
                    # Store the response into scenario
                    scenario["messages"].append({"role": "Actor", "content": response})
                    yield "DONE"
