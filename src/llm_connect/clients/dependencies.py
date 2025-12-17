from fastapi import Request


def get_llm(request: Request):
    return request.app.state.llm


def get_postgre_pool(request: Request):
    return request.app.state.pool


def get_redis(request: Request):
    return request.app.state.redis


def get_http_client(request: Request):
    return request.app.state.http_client


def get_s3_session(request: Request):
    return request.app.state.s3_session
