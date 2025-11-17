from fastapi import APIRouter, Depends

from llm_connect.auth import verify_token
from llm_connect.types import Payload

router = APIRouter(prefix="/api/v1/private", tags=["private"])


@router.get("/")
async def get(payload: Payload = Depends(verify_token)):
    return {"user_id": payload["sub"]}
