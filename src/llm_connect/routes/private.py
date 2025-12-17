from asyncpg import Pool
from fastapi import APIRouter, Depends

from llm_connect.auth import verify_token
from llm_connect.clients.dependencies import get_postgre_pool
from llm_connect.services.learner_service import sync_learner
from llm_connect.types import Payload

router = APIRouter(prefix="/api/v1/private", tags=["private"])


@router.get("/")
async def get(
    payload: Payload = Depends(verify_token), pool: Pool = Depends(get_postgre_pool)
):
    await sync_learner(payload["sub"], pool)
    return {"user_id": payload["sub"]}
