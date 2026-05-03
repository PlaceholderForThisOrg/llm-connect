from datetime import datetime
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from llm_connect.auth.auth import verify_token
from llm_connect.clients.dependencies import (
    get_conversation_service,
    get_db_session,
    get_message_service,
)
from llm_connect.schemas.conversation_schema import (
    GetHelpResponse,
    PostMessageRequest,
    PostMessageResponse,
)
from llm_connect.schemas.pagination import CursorPaginatedResponse, PaginatedResponse
from llm_connect.services.ConversationService import ConversationService
from llm_connect.services.MessageService import MessageService
from llm_connect.types.auth import Payload

router = APIRouter(prefix="/api/v1/me/conversations", tags=["Conversations"])


@router.get(path="/{conversationId}/messages/")
async def get_messages(
    conversationId: UUID,
    cursor: Optional[datetime] = Query(None),
    limit: int = Query(20, le=100),
    service: MessageService = Depends(get_message_service),
):
    res = await service.get_conversation_messages(
        conversation_id=conversationId,
        cursor=cursor,
        limit=limit,
    )

    response = CursorPaginatedResponse(
        items=res["items"],
        nextCursor=res["next_cursor"],
    )

    return response


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
    # request: CreateConversationRequest,
    service: ConversationService = Depends(get_conversation_service),
    payload: Payload = Depends(verify_token),
):
    learner_id = payload["sub"]
    conversation_type = "NORMAL"
    conversation_title = "There is no title"
    res = await service.create_conversation(
        learner_id=learner_id,
        title=conversation_title,
        type=conversation_type,
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

    res = await service.stream_chat(
        conversation_id=conversationId,
        user_input=request.content,
        learner_id=learner_id,
    )

    response = PostMessageResponse(
        conversationId=conversationId,
        content=res["content"],
    )

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
