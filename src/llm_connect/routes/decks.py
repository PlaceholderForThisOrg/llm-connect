from uuid import UUID

from asyncpg import Pool
from fastapi import APIRouter, Depends

from llm_connect.auth.auth import verify_token
from llm_connect.clients.dependencies import get_postgre_pool
from llm_connect.schemas.deck_schema import (
    CreateDeckRequest,
    CreateDeckResponse,
    DeleteDeckResponse,
    GetDeckSummary,
)
from llm_connect.schemas.pagination import ListResponse, PaginationParams
from llm_connect.services.deck_service import (
    create_new_deck,
    fetch_all_deck,
    remove_deck,
)
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
async def get_all_decks(
    params: PaginationParams = Depends(),
    jwt_payload: Payload = Depends(verify_token),
    pool: Pool = Depends(get_postgre_pool),
) -> ListResponse[GetDeckSummary]:
    user_id = jwt_payload["sub"]

    data, meta = await fetch_all_deck(params, user_id, pool)

    data = [
        GetDeckSummary(
            id=row["id"],
            name=row["name"],
            description=row["description"],
            is_shared=row["is_shared"],
        )
        for row in data
    ]

    return ListResponse(data=data, meta=meta)


@router.delete("/{id}")
async def delete_deck(
    id: UUID,
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
async def update_deck(id: UUID, jwt_payload: Payload = Depends(verify_token)):
    None
