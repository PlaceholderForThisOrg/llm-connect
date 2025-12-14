from asyncpg import Pool
from fastapi import HTTPException

from llm_connect.schemas.deck_schema import CreateDeckRequest


async def create_new_deck(deck: CreateDeckRequest, user_id: str, pool: Pool):
    sql = """
    INSERT INTO srs.deck (user_id, name, description)
    VALUES ($1, $2, $3)
    RETURNING id, name, description, is_shared
    """

    async with pool.acquire() as conn:
        row = await conn.fetchrow(sql, user_id, deck.name, deck.description)
        return row


async def remove_deck(user_id: str, id: int, pool: Pool):
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


async def fetch_all_deck(pool: Pool):
    None
