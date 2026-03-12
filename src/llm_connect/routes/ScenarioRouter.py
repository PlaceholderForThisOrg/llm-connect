from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse

from llm_connect.auth.auth import verify_token
from llm_connect.clients.dependencies import get_chat_service
from llm_connect.schemas.scenario_schema import ImmerseScenarioRequest
from llm_connect.services.ChatService import ChatService
from llm_connect.types.auth import Payload

router = APIRouter(prefix="/api/v1/me/scenarios", tags=["Scenario"])


@router.post(path="/", response_model=None, description="Continue the scenario")
async def immerse(
    request: ImmerseScenarioRequest,
    payload: Payload = Depends(verify_token),
    chat_service: ChatService = Depends(get_chat_service),
):
    user_id = payload["sub"]
    input = request.message
    # async for token in chat_service.scenario_immerse(input, 1):
    #     yield token
    return StreamingResponse(
        chat_service.scenario_immerse(input, 1), media_type="text/event-stream"
    )
