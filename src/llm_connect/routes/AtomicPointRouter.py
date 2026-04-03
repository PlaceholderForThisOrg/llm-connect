from aiohttp import Payload
from fastapi import APIRouter, Depends

from llm_connect.auth.auth import verify_token

router = APIRouter(prefix="/api/v1/atomic-points", tags=["Atomic points"])


@router.post("/")
async def create_point(
    # payload: Payload = Depends(verify_token),
):
    return {"message": "OK"}
