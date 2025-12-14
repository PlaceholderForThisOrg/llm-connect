from asyncpg import Pool
from fastapi import APIRouter, Depends

from llm_connect.auth.auth import verify_token
from llm_connect.clients.dependencies import get_postgre_pool
from llm_connect.schemas.deck_schema import (
    CreateDeckRequest,
    CreateDeckResponse,
    DeleteDeckResponse,
)
from llm_connect.services.deck_service import create_new_deck, remove_deck
from llm_connect.types.auth import Payload

router = APIRouter(prefix="/api/v1/learners/me/decks", tags=["Decks"])


@router.post("")
async def create_deck(
    payload: CreateDeckRequest,
    jwt_payload: Payload = Depends(verify_token),
    pool: Pool = Depends(get_postgre_pool),
) -> CreateDeckResponse:
    user_id = jwt_payload["sub"]
    data = await create_new_deck(payload, user_id, pool)

    return CreateDeckResponse(
        id=data["id"],
        name=data["name"],
        description=data["description"],
        is_shared=data["is_shared"],
    )


@router.get("")
async def get_all_decks(jwt_payload: Payload = Depends(verify_token)):
    None


@router.delete("/{id}")
async def delete_deck(
    id: int,
    jwt_payload: Payload = Depends(verify_token),
    pool: Pool = Depends(get_postgre_pool),
) -> DeleteDeckResponse:
    user_id = jwt_payload["sub"]
    data = await remove_deck(user_id, id, pool)

    return DeleteDeckResponse(
        id=data["id"],
        name=data["name"],
        description=data["description"],
        is_shared=data["is_shared"],
    )


@router.patch("/{id}")
async def update_deck(jwt_payload: Payload = Depends(verify_token)):
    None
