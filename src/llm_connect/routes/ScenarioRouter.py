from fastapi import APIRouter, Depends

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
    input = request.message
    return await chat_service.scenario_immerse(input, 1)
