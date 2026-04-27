from typing import Optional

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from llm_connect.auth.auth import verify_token
from llm_connect.clients.dependencies import (
    get_conversation_service,
    get_db_session,
)
from llm_connect.schemas.conversation_schema import (
    CreateConversationRequest,
    GetHelpResponse,
    PostMessageRequest,
)
from llm_connect.schemas.pagination import PaginatedResponse
from llm_connect.services.ConversationService import ConversationService
from llm_connect.types.auth import Payload

router = APIRouter(prefix="/api/v1/me/conversations", tags=["Conversations"])


@router.get(path="/")
async def search_conversations(
    search: Optional[str] = None,
    page: int = 1,
    page_size: int = 10,
    service: ConversationService = Depends(get_conversation_service),
    payload: Payload = Depends(verify_token),
):
    learner_id = payload["sub"]
    res = await service.get_conversations(
        learner_id=learner_id,
        search=search,
        page=page,
        page_size=page_size,
    )

    response = PaginatedResponse(
        items=res["items"],
        page=res["page"],
        pageSize=res["page_size"],
        total=res["total"],
    )

    return response


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


@router.post(path="/{conversationId}/messages/")
async def chat(
    conversationId: str,
    request: PostMessageRequest,
    service: ConversationService = Depends(get_conversation_service),
    payload: Payload = Depends(verify_token),
    session: AsyncSession = Depends(get_db_session),
):
    learner_id = payload["sub"]
    # message = request.content

    async def token_stream():
        try:

            async for chunk in service.stream_chat(
                conversation_id=conversationId,
                user_input=request.content,
                learner_id=learner_id,
            ):
                yield chunk

            await session.commit()

        except Exception:
            await session.rollback()

    return StreamingResponse(
        token_stream(),
        media_type="text/plain",
    )


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
