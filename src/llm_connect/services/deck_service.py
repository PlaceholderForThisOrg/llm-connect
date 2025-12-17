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


async def get_deck_reviews_service(
    *,
    pool: Pool,
    deck_id: UUID,
    user_id: str,
    limit: int,
    # offset: int,
):
    async with pool.acquire() as conn:
        async with conn.transaction():
            count_sql = """
            SELECT COUNT(*)
            FROM srs.deck d
            JOIN srs.card c ON c.deck_id = d.id
            JOIN srs.learner_card lc ON lc.card_id = c.id
            WHERE d.id = $1
              AND lc.user_id = $2
              AND (lc.next_review IS NULL OR lc.next_review <= NOW())
            """

            total = await conn.fetchval(
                count_sql,
                deck_id,
                user_id,
            )

            data_sql = """
            SELECT
                lc.id               AS learner_card_id,
                c.id                AS card_id,
                c.front,
                c.back,
                lc.state,
                lc.interval,
                lc.repetitions,
                lc.ease_factor,
                lc.next_review,
                lc.last_reviewed
            FROM srs.deck d
            JOIN srs.card c ON c.deck_id = d.id
            JOIN srs.learner_card lc ON lc.card_id = c.id
            WHERE d.id = $1
              AND lc.user_id = $2
              AND (lc.next_review IS NULL OR lc.next_review <= NOW())
            ORDER BY lc.next_review NULLS FIRST
            LIMIT $3;
            """

            rows = await conn.fetch(
                data_sql,
                deck_id,
                user_id,
                limit,
                # offset,
            )

    return total, rows
