from uuid import UUID

from asyncpg import Pool
from fastapi import HTTPException

from llm_connect.schemas.deck_schema import CreateDeckRequest
from llm_connect.schemas.pagination import PaginationParams
from llm_connect.services.shared import get_offset, make_meta


async def create_new_deck(deck: CreateDeckRequest, user_id: str, pool: Pool):
    sql = """
    INSERT INTO srs.deck (user_id, name, description)
    VALUES ($1, $2, $3)
    RETURNING id, name, description, is_shared
    """

    async with pool.acquire() as conn:
        row = await conn.fetchrow(sql, user_id, deck.name, deck.description)
        return row


async def remove_deck(user_id: str, id: UUID, pool: Pool):
    sql = """
    DELETE FROM srs.deck AS d
    WHERE d.user_id = $1 AND d.id = $2
    RETURNING *
    """
    async with pool.acquire() as conn:
        row = await conn.fetchrow(sql, user_id, id)
        if row is None:
            raise HTTPException(status_code=404, detail="Deck is not found")

        return row


async def fetch_all_deck(params: PaginationParams, user_id: str, pool: Pool):
    count_sql = """
    SELECT COUNT(*)
    FROM srs.deck AS d
    WHERE d.user_id = $1
    """

    sql = """
    SELECT d.id, d.name, d.description, d.is_shared
    FROM srs.deck AS d
    WHERE d.user_id = $1
    ORDER BY created_at DESC
    LIMIT $2 OFFSET $3
    """

    offset = get_offset(params)

    async with pool.acquire() as conn:
        total_items = await conn.fetchval(count_sql, user_id)

        rows = await conn.fetch(
            sql,
            user_id,
            params.limit,
            offset,
        )

        meta = make_meta(params, total_items)

        return rows, meta
