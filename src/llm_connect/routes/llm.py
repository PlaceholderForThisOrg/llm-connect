import asyncio

from azure.ai.inference.models import SystemMessage, UserMessage
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse

from llm_connect.auth import verify_token
from llm_connect.clients.llm import LLM
from llm_connect.configs import llm
from llm_connect.models.MessageStream import Role
from llm_connect.schemas import chat_schema
from llm_connect.services.chat_service import push_message, stream
from llm_connect.types.auth import Payload

router = APIRouter(prefix="/api/v1/companion", tags=["Companion"])


@router.post("/chat")
def generate(request: chat_schema.ChatRequest):
    response = LLM.complete(
        messages=[
            SystemMessage("You are an English companion"),
            UserMessage(request.message),
        ],
        temperature=1.0,
        top_p=1.0,
        model=llm.MODEL,
        stream=False,
    )
    return chat_schema.ChatResponse(message=response.choices[0].message.content)


@router.post("/chat-stream")
async def generate_stream(
    request: chat_schema.ChatRequest, payload: Payload = Depends(verify_token)
):
    asyncio.create_task(push_message(request.message, payload["sid"], Role.LEARNER))
    # await push_message(request.message, payload["sid"], Role.LEARNER)
    return StreamingResponse(
        stream(request.message, payload["sid"]), media_type="text/event-stream"
    )
