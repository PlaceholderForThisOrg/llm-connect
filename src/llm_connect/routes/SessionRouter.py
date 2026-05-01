from datetime import datetime
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, Depends
from fastapi.responses import StreamingResponse

from llm_connect.auth.auth import verify_token
from llm_connect.clients.dependencies import (
    get_chat_service,
    get_session_service,
)
from llm_connect.models.Activity import TaskType
from llm_connect.schemas.pagination import PaginatedResponse
from llm_connect.schemas.session_schema import (
    CreateSessionRequest,
    GetAllSessionResponse,
    GetGoalResponse,
    Interaction,
    SessionSearchQuery,
    SubmitInteraction,
)
from llm_connect.services.ChatService import ChatService
from llm_connect.services.SessionService import SessionService
from llm_connect.types.auth import Payload

router = APIRouter(prefix="/api/v1/me/sessions", tags=["Session"])


@router.get("/{sessionId}/messages")
async def fetch_messages_in_role_play_activity(
    session_id: UUID,
    cursor: Optional[datetime] = None,
    limit: int = 10,
    service: SessionService = Depends(get_session_service),
):
    interactions = await service.get_interactions_by_session(session_id, cursor, limit)

    messages = service.flatten_interactions(interactions)

    return service.paginate(messages, limit)


@router.get("/{sessionId}")
async def get_session_detail(
    sessionId: str,
    service: SessionService = Depends(get_session_service),
    payload: Payload = Depends(verify_token),
):
    learner_id = str(payload["accountId"])

    if not learner_id:
        learner_id = payload["sub"]

    return await service.get_session_detail(
        session_id=sessionId,
        learner_id=learner_id,
    )


@router.get("/")
async def search_sessions(
    activity_id: str | None = None,
    status: str | None = None,
    # learner_id: str | None = None,
    started_from: str | None = None,
    started_to: str | None = None,
    min_score: float | None = None,
    max_score: float | None = None,
    page: int = 1,
    page_size: int = 20,
    service: SessionService = Depends(get_session_service),
    payload: Payload = Depends(verify_token),
):
    learner_id = str(payload["accountId"])

    if not learner_id:
        learner_id = payload["sub"]

    query = SessionSearchQuery(
        activity_id=activity_id,
        status=status,
        learner_id=learner_id,
        started_from=started_from,
        started_to=started_to,
        min_score=min_score,
        max_score=max_score,
        page=page,
        page_size=page_size,
    )

    res = await service.search_sessions(query)

    response = PaginatedResponse(
        items=[GetAllSessionResponse.model_validate(s) for s in res["items"]],
        total=res["total"],
        page=res["page"],
        pageSize=res["page_size"],
    )

    return response


@router.post("/{sessionId}/progresses/{taskId}/interactions/")
async def submit_interaction(
    sessionId: str,
    taskId: str,
    request: SubmitInteraction,
    payload: Payload = Depends(verify_token),
    service: SessionService = Depends(get_session_service),
):
    learner_id = str(payload["accountId"])

    if not learner_id:
        learner_id = payload["sub"]

    task_type = request.type

    if task_type == TaskType.GENERATE:

        async def token_stream():

            async for chunk in service.submit_interaction_stream(
                learner_id=learner_id,
                session_id=sessionId,
                task_id=taskId,
                interaction=request.interaction,
                answer=request.answer,
            ):
                yield chunk

        return StreamingResponse(
            token_stream(),
            media_type="text/plain",
        )

    else:
        # Normal task
        res = await service.submit_interaction(
            learner_id=learner_id,
            session_id=sessionId,
            task_id=taskId,
            interaction=None,
            answer=request.answer,
        )

        response = res

        return response


# @router.get("/{sessionId}/progresses/{taskId}/interactions/")
# def get_all_interactions(
#     sessionId: str,
#     taskId: str,
#     payload: Payload = Depends(verify_token),
# ):
#     learner_id = payload["sub"]


@router.get("/{sessionId}/current-task")
async def get_current_task(
    sessionId: str,
    service: SessionService = Depends(get_session_service),
    payload: Payload = Depends(verify_token),
):
    return await service.get_current_task(sessionId)


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


@router.post("")
async def create_session_from_activity(
    request: CreateSessionRequest,
    service: SessionService = Depends(get_session_service),
    payload: Payload = Depends(verify_token),
):
    learner_id = str(payload["accountId"])

    if not learner_id:
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
