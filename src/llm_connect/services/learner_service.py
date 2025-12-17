import aioboto3
import asyncpg
from asyncpg import Pool
from fastapi import HTTPException, UploadFile

from llm_connect import logger
from llm_connect.configs.s3 import ENDPOINT_URL, SERVICE_NAME
from llm_connect.schemas.learner_schema import LearnerUpdateRequest


async def sync_learner(user_id: str, pool: Pool):
    sql = """
    SELECT l.user_id
    FROM learner l
    WHERE l.user_id = $1
    """
    async with pool.acquire() as conn:
        row = await conn.fetchrow(sql, user_id)

        if row is None:
            await conn.execute(
                """
                INSERT INTO learner (user_id)
                VALUES ($1)
                """,
                user_id,
            )
            logger.logger.info(f"{user_id} is synchronized")


async def update_avatar(
    file: UploadFile, user_id: str, s3_session: aioboto3.Session, pool: asyncpg.Pool
):
    bucket = "avatars"
    key = f"{user_id}.png"
    avatar_url = await upload_file(key, file, s3_session, bucket)
    async with pool.acquire() as conn:
        sql = """
        UPDATE learner
        SET avatar_url = $1, updated_at = NOW()
        WHERE user_id = $2
        """
        await conn.execute(
            sql,
            avatar_url,
            user_id,
        )

    logger.logger.info("Update avatar_url in database")

    return avatar_url


async def upload_file(
    key: str, file: UploadFile, s3_session: aioboto3.Session, bucket: str
) -> str:
    async with s3_session.client(
        service_name=SERVICE_NAME,
        endpoint_url=ENDPOINT_URL(),
    ) as s3_client:
        await s3_client.upload_fileobj(
            file.file,
            bucket,
            key,
            ExtraArgs={"ContentType": file.content_type},
        )

    logger.logger.info("Upload avatar into MiniO")

    tem_url = await generate_avatar_url(bucket, key, s3_session)
    return tem_url


async def generate_avatar_url(
    bucket: str,
    key: str,
    s3_session,
    expires_in: int = 3600,
) -> str:
    async with s3_session.client(
        service_name=SERVICE_NAME,
        endpoint_url=ENDPOINT_URL(),
    ) as s3_client:
        return await s3_client.generate_presigned_url(
            "get_object",
            Params={
                "Bucket": bucket,
                "Key": key,
            },
            ExpiresIn=expires_in,
        )


async def update_learner(
    user_id: str, pool: asyncpg.Pool, payload: LearnerUpdateRequest
):
    sql = """
    UPDATE learner
    SET
        name = COALESCE($1, name),
        nickname = COALESCE($2, nickname),
        avatar_url = COALESCE($3, avatar_url),
        date_of_birth = COALESCE($4, date_of_birth),
        settings = CASE
            WHEN $5::jsonb IS NULL THEN settings
            ELSE settings || $5::jsonb
        END,
        updated_at = NOW()
    WHERE user_id = $6
    RETURNING *;
    """

    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            sql,
            payload.name,
            payload.nickname,
            payload.avatar_url,
            payload.date_of_birth,
            payload.settings,
            user_id,
        )

    if not row:
        raise HTTPException(status_code=404, detail="Learner not found")

    return row


async def fetch_learner(user_id: str, pool: asyncpg.Pool):
    sql = """
    SELECT l.user_id, l.name, l.nickname, l.avatar_url, l.date_of_birth, l.settings
    FROM learner as l
    WHERE l.user_id = $1
    """
    async with pool.acquire() as conn:
        row = await conn.fetchrow(sql, user_id)

        if not row:
            raise HTTPException(status_code=404, detail="Learner not found")

        return row
