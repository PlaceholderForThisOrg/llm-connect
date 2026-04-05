from fastapi import APIRouter, Depends

from llm_connect.clients.dependencies import get_conversation_service
from llm_connect.schemas.conversation_schema import (
    PostMessageRequest,
    PostMessageResponse,
)
from llm_connect.services.ConversationService import ConversationService

router = APIRouter(prefix="/api/v1/me/conversations", tags=["Conversations"])


@router.post(path="/")
async def create_new_conversation():
    pass


@router.post(path="/{con_id}/messages/")
async def chat(
    con_id: str,
    request: PostMessageRequest,
    con_ser: ConversationService = Depends(get_conversation_service),
):
    learner_id = "learner_001"
    re_message = await con_ser.chat(
        learner_id,
        con_id,
        request.content,
    )

    response = PostMessageResponse(content=re_message["content"])

    return response
