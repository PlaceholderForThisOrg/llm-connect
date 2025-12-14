from uuid import UUID

from asyncpg import Pool
from fastapi import APIRouter, Depends

from llm_connect.auth.auth import verify_token
from llm_connect.clients.dependencies import get_postgre_pool
from llm_connect.types.auth import Payload

router = APIRouter(prefix="/api/v1/learners/me/decks/{deck_id}/cards")


@router.post(path="")
async def create_card_in_deck(
    deck_id: UUID,
    jwt_payload: Payload = Depends(verify_token),
    pool: Pool = Depends(get_postgre_pool),
):
    None
