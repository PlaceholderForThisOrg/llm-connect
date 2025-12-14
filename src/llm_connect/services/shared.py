import math

from llm_connect.schemas.pagination import PaginationMeta, PaginationParams


def get_offset(params: PaginationParams) -> int:
    return (params.page - 1) * params.limit


def make_meta(params: PaginationParams, total_items: int) -> PaginationMeta:
    total_pages = math.ceil(total_items / params.limit)

    meta = PaginationMeta(
        page=params.page,
        limit=params.limit,
        total_items=total_items,
        total_pages=total_pages,
        has_more=params.page < total_pages,
    )

    return meta


# async def upload_file(
#     key: str, file: UploadFile, s3_session: aioboto3.Session, bucket: str
# ) -> str:
#     async with s3_session.client(
#         service_name=SERVICE_NAME,
#         endpoint_url=ENDPOINT_URL(),
#     ) as s3_client:
#         await s3_client.upload_fileobj(
#             file.file,
#             bucket,
#             key,
#             ExtraArgs={"ContentType": file.content_type},
#         )

#     logger.logger.info("Upload media into MiniO")

#     tem_url = await generate_avatar_url(bucket, key, s3_session)
#     return tem_url
