import httpx
from asyncpg import Pool
from fastapi import APIRouter, Depends

from llm_connect.clients.dependencies import get_http_client, get_postgre_pool
from llm_connect.schemas.dictionary_schema import DictionaryResponse
from llm_connect.services.dictionary_service import look_up

router = APIRouter(prefix="/api/v1/dictionary", tags=["Dictionary"])


@router.get("")
async def look_up_a_word(
    word: str = "",
    pool: Pool = Depends(get_postgre_pool),
    http_client: httpx.AsyncClient = Depends(get_http_client),
) -> DictionaryResponse:
    entry = await look_up(word=word.lower(), pool=pool, http_client=http_client)
    response = DictionaryResponse(**entry)
    return response
