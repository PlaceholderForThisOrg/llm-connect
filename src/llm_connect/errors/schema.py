from typing import TypedDict


class ErrorResponse(TypedDict):
    status: int
    message: str
    details: str
