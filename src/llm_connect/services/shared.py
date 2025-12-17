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
