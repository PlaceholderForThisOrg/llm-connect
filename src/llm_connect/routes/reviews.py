from uuid import UUID

from asyncpg import Pool
from fastapi import APIRouter, Depends, HTTPException

from llm_connect.auth.auth import verify_token
from llm_connect.clients.dependencies import get_postgre_pool
from llm_connect.schemas.deck_schema import SubmitReviewRequest, SubmitReviewResponse
from llm_connect.services.reviews_service import review
from llm_connect.types.auth import Payload

router = APIRouter(prefix="/api/v1/reviews", tags=["Spaced repetition System"])


@router.post(
    "/{learner_card_id}",
    response_model=SubmitReviewResponse,
)
async def submit_review(
    learner_card_id: UUID,
    body: SubmitReviewRequest,
    jwt_payload: Payload = Depends(verify_token),
    pool: Pool = Depends(get_postgre_pool),
):

    user_id = jwt_payload["sub"]

    try:
        row = await review(
            pool=pool,
            learner_card_id=learner_card_id,
            user_id=user_id,
            quality=body.quality,
        )
    except ValueError:
        raise HTTPException(status_code=404, detail="Card not found")

    return SubmitReviewResponse(
        learner_card_id=row["id"],
        state=row["state"],
        interval=row["interval"],
        repetitions=row["repetitions"],
        ease_factor=row["ease_factor"],
        next_review=row["next_review"],
    )
