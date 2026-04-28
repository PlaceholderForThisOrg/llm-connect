from fastapi import APIRouter, BackgroundTasks, Depends

from llm_connect.auth.auth import verify_token
from llm_connect.clients.dependencies import get_chat_service, get_session_service
from llm_connect.schemas.session_schema import (
    CreateSessionRequest,
    GetGoalResponse,
    Interaction,
)
from llm_connect.services.ChatService import ChatService
from llm_connect.services.SessionService import SessionService
from llm_connect.types.auth import Payload

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


@router.post(
    "",
)
async def create_session_from_activity(
    request: CreateSessionRequest,
    service: SessionService = Depends(get_session_service),
    payload: Payload = Depends(verify_token),
):
    learner_id = payload["sub"]

    res = await service.create_session_from_activity(
        activity_id=request.activityId,
        learner_id=learner_id,
    )

    response = res

    return response


# @router.post(
#     "",
# )
# async def create(
#     # activity_id: str,
#     request: CreateSessionRequest,
#     session_service: SessionService = Depends(get_session_service),
# ):
#     # TODO: Initialize the sessionID
#     # in the database, manage the cache
#     # layer
#     activity_id = request.activityId
#     session = session_service.new_session("", activity_id)

#     response = CreateSessionResponse(
#         sessionId=session["session_id"],
#         conId=session["con_id"],
#     )
#     return response


@router.get("/{session_id}/goals", response_model=GetGoalResponse)
async def get_goal(
    session_id: str,
    session_service: SessionService = Depends(get_session_service),
):
    # TODO: Get the current goal for the
    # learner to try
    activity = session_service.get_session(session_id)
    goal, status = await session_service.get_current_goal(session_id)

    response = GetGoalResponse(
        sessionId=session_id,
        activityId=activity["activity_id"],
        goal=goal,
        status=status,
    )

    return response
