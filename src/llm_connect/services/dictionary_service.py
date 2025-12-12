from urllib.parse import urljoin

import httpx
from asyncpg import Pool
from fastapi import HTTPException

from llm_connect import logger
from llm_connect.configs.free_dict import URL
from llm_connect.schemas.dictionary_schema import DictionaryEntry


async def look_up(word: str, pool: Pool, http_client: httpx.AsyncClient):
    entries = await look_up_free(word, http_client)
    return entries


async def look_up_db(word: str, pool: Pool):
    None


async def look_up_free(word: str, http_client: httpx.AsyncClient):
    url = urljoin(URL, word)
    logger.logger.debug(f"Built URL is {url}")
    response = await http_client.get(url=url)

    if response.status_code == 404:
        raise HTTPException(
            status_code=404, detail=f"{word} is not found in the dictionary"
        )

    data = response.json()
    return [DictionaryEntry(**item) for item in data]
