from fastapi import APIRouter, BackgroundTasks, Depends
from fastapi.responses import StreamingResponse

from llm_connect.auth.auth import verify_token
from llm_connect.clients.dependencies import get_chat_service, get_session_service
from llm_connect.schemas.session_schema import Interaction
from llm_connect.services.ChatService import ChatService
from llm_connect.services.SessionService import SessionService
from llm_connect.types.auth import Payload

router = APIRouter(prefix="/api/v1/me/sessions", tags=["Session"])


@router.post("/{session_id}")
async def interact(
    request: Interaction,
    session_id: int,
    engine: BackgroundTasks,
    payload: Payload = Depends(verify_token),
    chat_service: ChatService = Depends(get_chat_service),
    session_service: SessionService = Depends(get_session_service),
):
    # logger.info("⚔️ Router")
    content = request.content

    return StreamingResponse(
        content=session_service.handle_interact(
            session_id,
            content,
            engine,
        ),
        media_type="text/event-stream",
    )

    return StreamingResponse(
        content=chat_service.scenario_immerse(content, 1, engine),
        media_type="text/event-stream",
    )
