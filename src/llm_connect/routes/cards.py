from uuid import UUID

from asyncpg import Pool
from fastapi import APIRouter, Depends

from llm_connect.auth.auth import verify_token
from llm_connect.clients.dependencies import get_postgre_pool
from llm_connect.schemas.cards_schema import AddCardRequest, AddCardResponse
from llm_connect.services.cards_service import add_card
from llm_connect.types.auth import Payload

router = APIRouter(
    prefix="/api/v1/learners/me/decks/{deck_id}/cards", tags=["Flashcards"]
)


@router.post(path="")
async def create_card_in_deck(
    deck_id: UUID,
    payload: AddCardRequest,
    jwt_payload: Payload = Depends(verify_token),
    pool: Pool = Depends(get_postgre_pool),
) -> AddCardResponse:
    user_id = jwt_payload["sub"]

    data = await add_card(deck_id, payload, user_id, pool)

    return AddCardResponse(id=data["id"], front=data["front"], back=data["back"])
