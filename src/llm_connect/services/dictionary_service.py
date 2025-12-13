from urllib.parse import urljoin

import httpx
from asyncpg import Pool
from fastapi import HTTPException

from llm_connect import logger
from llm_connect.configs.free_dict import URL


async def look_up(word: str, pool: Pool, http_client: httpx.AsyncClient):
    # 1. look up in the main database
    entry = await look_up_db(word, pool)

    if entry is None:
        # 2. None, call free dictionary
        logger.logger.info(f"Get {word} from free dictionary")
        free_entries = await look_up_free(word, http_client)
        # 3. Cache the entry
        await cache_entry(free_entries, pool)
        return free_entries[0]

    logger.logger.info(f"Get {word} from database")
    return entry


async def cache_entry(entries, pool: Pool):
    sql = """
    INSERT INTO dictionary (word, phonetic, phonetics, meanings, raw_payload)
    VALUES ($1, $2, $3::jsonb, $4::jsonb, $5::jsonb)
    """
    first_entry = entries[0]
    phonetics = first_entry["phonetics"]
    meanings = first_entry["meanings"]

    async with pool.acquire() as conn:
        await conn.execute(
            sql,
            first_entry["word"],
            first_entry.get("phonetic", None),
            phonetics,
            meanings,
            entries,
        )

    logger.logger.info(f"Store {first_entry["word"]} into database")


async def look_up_db(word: str, pool: Pool):
    sql = """
    SELECT d.id, d.word, d.phonetic, d.phonetics, d.meanings
    FROM dictionary as d
    WHERE d.word = $1
    """

    async with pool.acquire() as conn:
        row = await conn.fetchrow(sql, word)
        if row is None:
            # fetch data from free API
            # store it into the database
            return None

        return row


async def look_up_free(word: str, http_client: httpx.AsyncClient):
    url = urljoin(URL, word)
    logger.logger.debug(f"Built URL is {url}")
    response = await http_client.get(url=url)

    if response.status_code == 404:
        raise HTTPException(
            status_code=404, detail=f"{word} is not found in the dictionary"
        )

    return response.json()
