from fastapi import APIRouter, Depends

from llm_connect.clients.dependencies import (
    get_conversation_repo,
    get_conversation_service,
)
from llm_connect.repositories.ConversationRepository import ConversationRepository
from llm_connect.schemas.conversation_schema import (
    PostConRequest,
    PostConResponse,
    PostMessageRequest,
    PostMessageResponse,
)
from llm_connect.services.ConversationService import ConversationService

router = APIRouter(prefix="/api/v1/me/conversations", tags=["Conversations"])


@router.post(path="/")
def create_new_conversation(
    request: PostConRequest,
    con_repo: ConversationRepository = Depends(get_conversation_repo),
):
    id = con_repo.create_new_conversation(request.type)

    return PostConResponse(conId=id)


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
