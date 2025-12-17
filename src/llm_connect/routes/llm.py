import asyncio

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse

from llm_connect.auth import verify_token
from llm_connect.clients.dependencies import get_llm, get_redis
from llm_connect.models.MessageStream import Role
from llm_connect.schemas import chat_schema
from llm_connect.services.chat_service import push_message, stream
from llm_connect.types.auth import Payload

router = APIRouter(prefix="/api/v1/companion", tags=["Companion"])


@router.post("/chat-stream")
async def generate_stream(
    request: chat_schema.ChatRequest,
    payload: Payload = Depends(verify_token),
    llm=Depends(get_llm),
    redis=Depends(get_redis),
):
    asyncio.create_task(
        push_message(request.message, payload["sid"], Role.LEARNER, redis=redis)
    )
    return StreamingResponse(
        stream(request.message, payload["sid"], llm=llm, redis=redis),
        media_type="text/event-stream",
    )
