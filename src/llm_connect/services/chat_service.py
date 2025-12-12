import asyncio
import time

from azure.ai.inference.models import SystemMessage, UserMessage

from llm_connect.configs.llm import MODEL
from llm_connect.configs.redis import MESSAGE_STREAM
from llm_connect.models.MessageStream import MessageStream, Role


async def stream(user_message: str, user_id: str, llm, redis):
    response = llm.complete(
        messages=[
            SystemMessage("You are an English companion"),
            UserMessage(user_message),
        ],
        temperature=1.0,
        top_p=1.0,
        model=MODEL,
        stream=True,
    )

    companion_messages = []

    for chunk in response:
        if chunk and chunk.choices:
            delta = chunk.choices[0].delta.content or ""
            if delta:
                companion_messages.append(delta)
                yield delta

    companion_messages = "".join(companion_messages)

    asyncio.create_task(
        push_message(companion_messages, user_id, Role.COMPANION, redis=redis)
    )
    yield "[END]"


async def push_message(content: str, user_id: str, role: Role, redis):
    message = MessageStream(
        user_id=user_id,
        role=str(role),
        content=content,
        timestamp=str(int(time.time() * 1000)),
    )

    await redis.xadd(MESSAGE_STREAM, fields=message.model_dump())
