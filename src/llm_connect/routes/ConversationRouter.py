from fastapi import APIRouter, Depends

from llm_connect.auth.auth import verify_token
from llm_connect.clients.dependencies import (
    get_conversation_service,
)
from llm_connect.schemas.conversation_schema import (
    CreateConversationRequest,
    GetHelpResponse,
    PostMessageRequest,
    PostMessageResponse,
)
from llm_connect.services.ConversationService import ConversationService
from llm_connect.types.auth import Payload

router = APIRouter(prefix="/api/v1/me/conversations", tags=["Conversations"])


@router.post(path="/")
async def create_conversation(
    request: CreateConversationRequest,
    service: ConversationService = Depends(get_conversation_service),
    payload: Payload = Depends(verify_token),
):
    learner_id = payload["sub"]
    res = await service.create_conversation(
        learner_id=learner_id,
        title=request.title,
        type=request.type,
    )

    # FIXME: map the model to the DTO
    response = res

    return response


# @router.post(path="/")
# def create_new_conversation(
#     request: PostConRequest,
#     con_repo: ConversationRepository = Depends(get_conversation_repo),
# ):
#     id = con_repo.create_new_conversation(request.type)

#     return PostConResponse(conId=id)


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


@router.get("/{con_id}/help/")
async def get_help(
    con_id: str,
    sesId: str,
    con_ser: ConversationService = Depends(get_conversation_service),
):

    ses_id = sesId

    content = await con_ser.sos(
        ses_id,
        con_id,
    )

    return GetHelpResponse(
        content=content,
    )
