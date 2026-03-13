import asyncio

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse

from llm_connect.auth import verify_token
from llm_connect.clients.dependencies import get_chat_service
from llm_connect.models.MessageStream import Role
from llm_connect.schemas import chat_schema
from llm_connect.services.ChatService import ChatService
from llm_connect.types.auth import Payload

router = APIRouter(prefix="/api/v1/companion", tags=["Companion"])


@router.post("/chat-stream")
async def generate_stream(
    request: chat_schema.ChatRequest,
    payload: Payload = Depends(verify_token),
    chat_service: ChatService = Depends(get_chat_service),
):
    asyncio.create_task(
        chat_service.push_message(request.message, payload["sub"], Role.LEARNER)
    )

    return StreamingResponse(
        chat_service.stream(request.message, payload["sub"]),
        media_type="text/event-stream",
    )
