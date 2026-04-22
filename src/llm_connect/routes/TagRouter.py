from fastapi import APIRouter, Depends

from llm_connect.auth.auth import verify_token
from llm_connect.types.auth import Payload

router = APIRouter(prefix="/api/v1/tags", tags=["Tags"])


@router.post("/")
async def create_tag(
    payload: Payload = Depends(verify_token),
):
    None
