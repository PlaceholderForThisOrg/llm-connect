from fastapi import APIRouter, BackgroundTasks, Depends
from fastapi.responses import StreamingResponse

from llm_connect.clients.dependencies import get_chat_service, get_session_service
from llm_connect.schemas.session_schema import Interaction
from llm_connect.services.ChatService import ChatService
from llm_connect.services.SessionService import SessionService

router = APIRouter(prefix="/api/v1/me/sessions", tags=["Session"])


@router.post("/{session_id}")
async def interact(
    request: Interaction,
    session_id: int,
    engine: BackgroundTasks,
    # payload: Payload = Depends(verify_token),
    chat_service: ChatService = Depends(get_chat_service),
    session_service: SessionService = Depends(get_session_service),
):
    # logger.info("⚔️ Router")
    content = request.content

    content = ""

    async for token in session_service.handle_interaction(session_id, content, engine):
        content += token

    return {"content": content}

    return StreamingResponse(
        content=session_service.handle_interaction(
            session_id,
            content,
            engine,
        ),
        media_type="text/event-stream",
    )
