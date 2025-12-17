from datetime import datetime, timedelta
from uuid import UUID

from asyncpg import Pool

from llm_connect.services.shared import sm2_update


async def review(
    *,
    pool: Pool,
    learner_card_id: UUID,
    user_id: str,
    quality: int,
):
    async with pool.acquire() as conn:
        async with conn.transaction():
            row = await conn.fetchrow(
                """
                SELECT
                    repetitions,
                    interval,
                    ease_factor
                FROM srs.learner_card
                WHERE id = $1
                  AND user_id = $2
                FOR UPDATE
                """,
                learner_card_id,
                user_id,
            )

            if not row:
                raise ValueError("Learner card not found")

            repetitions, interval, ease_factor = sm2_update(
                quality=quality,
                repetitions=row["repetitions"],
                interval=row["interval"],
                ease_factor=row["ease_factor"],
            )

            next_review = datetime.utcnow() + timedelta(days=interval)

            updated = await conn.fetchrow(
                """
                UPDATE srs.learner_card
                SET
                    repetitions = $1,
                    interval = $2,
                    ease_factor = $3,
                    last_reviewed = NOW(),
                    next_review = $4,
                    state = 'REVIEW'
                WHERE id = $5
                RETURNING
                    id,
                    state,
                    interval,
                    repetitions,
                    ease_factor,
                    next_review
                """,
                repetitions,
                interval,
                ease_factor,
                next_review,
                learner_card_id,
            )

    return updated
