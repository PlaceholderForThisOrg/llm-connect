from fastapi import Request
from fastapi.exceptions import HTTPException
from fastapi.responses import JSONResponse

from .schema import ErrorResponse


async def global_exception_handler(request: Request, exc: Exception):
    content = ErrorResponse(
        status=500, message="Internal Server Error", details=str(exc)
    )
    return JSONResponse(status_code=500, content=content)


async def http_exception_handler(request, exc: HTTPException):
    content = ErrorResponse(
        status=exc.status_code, message=exc.detail, details=str(exc)
    )
    return JSONResponse(
        status_code=exc.status_code,
        content=content,
    )
