from fastapi import APIRouter

router = APIRouter(prefix="/api/v1/public", tags=["public"])


@router.get("/")
async def get():
    return {"data": "Hello machine learning!"}
