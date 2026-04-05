from fastapi import APIRouter, BackgroundTasks, Depends

from llm_connect.clients.dependencies import get_chat_service, get_session_service
from llm_connect.schemas.session_schema import (
    CreateSessionResponse,
    GetGoalResponse,
    Interaction,
)
from llm_connect.services.ChatService import ChatService
from llm_connect.services.SessionService import SessionService

router = APIRouter(prefix="/api/v1/me/sessions", tags=["Session"])


# FIXME: Restful API's standard
@router.post("/{session_id}/loop")
async def interact(
    request: Interaction,
    session_id: str,
    engine: BackgroundTasks,
    # payload: Payload = Depends(verify_token),
    chat_service: ChatService = Depends(get_chat_service),
    session_service: SessionService = Depends(get_session_service),
):
    # logger.info("⚔️ Router")
    input = request.content

    output = ""

    async for token in session_service.handle_interaction(session_id, input, engine):
        output += token

    return {"content": output}

    # return StreamingResponse(
    #     content=session_service.handle_interaction(
    #         session_id,
    #         content,
    #         engine,
    #     ),
    #     media_type="text/event-stream",
    # )


@router.post("/{activity_id}", response_model=CreateSessionResponse)
async def create(
    # request: CreateSessionRequest,
    session_service: SessionService = Depends(get_session_service),
):
    # TODO: Initialize the sessionID
    # in the database, manage the cache
    # layer
    response = CreateSessionResponse(sessionId="session_002")
    return response


@router.get("/{session_id}/goals", response_model=GetGoalResponse)
async def get_goal(
    session_id: str,
    session_service: SessionService = Depends(get_session_service),
):
    # TODO: Get the current goal for the
    # learner to try
    goal, status = await session_service.get_current_goal("")

    response = GetGoalResponse(
        sessionId=session_id,
        activityId="activity_002",
        goal=goal,
        status=status,
    )

    return response
