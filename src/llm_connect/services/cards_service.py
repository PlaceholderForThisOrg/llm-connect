from uuid import UUID

from asyncpg import Pool
from fastapi import HTTPException

from llm_connect.schemas.cards_schema import AddCardRequest


async def init_srs_for_new_card(user_id: UUID, card_id: str, pool: Pool):
    sql = """
    INSERT INTO srs.learner_card
    (user_id, card_id)
    VALUES
    ($1, $2);
    """

    async with pool.acquire() as conn:
        await conn.execute(sql, user_id, card_id)


async def add_card(deck_id: UUID, payload: AddCardRequest, user_id: str, pool: Pool):
    sql = """
    INSERT INTO srs.card AS c (deck_id, front, back)
    SELECT d.id, $3, $4
    FROM srs.deck AS d
    WHERE d.id = $1
    AND d.user_id = $2
    RETURNING c.id, c.deck_id, c.front, c.back;
    """

    async with pool.acquire() as conn:
        row = await conn.fetchrow(sql, deck_id, user_id, payload.front, payload.back)

        if row is None:
            raise HTTPException(status_code=400, detail="Fail to add card to this deck")

    card_id = row["id"]
    await init_srs_for_new_card(user_id, card_id, pool)

    return row
