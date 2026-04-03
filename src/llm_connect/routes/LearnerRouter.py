import aioboto3
import asyncpg
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile

from llm_connect.auth.auth import verify_token
from llm_connect.clients.dependencies import (
    get_learner_service,
    get_postgre_pool,
    get_s3_session,
)
from llm_connect.schemas.learner_schema import (
    GetLearnerResponse,
    LearnerUpdateRequest,
    LearnerUpdateResponse,
    UploadAvatarResponse,
)
from llm_connect.services.LearnerService import (
    LearnerService,
    update_avatar,
    update_learner,
)
from llm_connect.types.auth import Payload

router = APIRouter(prefix="/api/v1/learners/me", tags=["Learner"])


@router.post("/avatar")
async def upload_avatar(
    file: UploadFile = File(),
    s3_session: aioboto3.Session = Depends(get_s3_session),
    pool: asyncpg.Pool = Depends(get_postgre_pool),
    # payload: Payload = Depends(verify_token),
) -> UploadAvatarResponse:
    if file.content_type not in {"image/png", "image/jpeg"}:
        raise HTTPException(400, "Unsupported image type")

    # user_id = payload["sub"]
    user_id = 1
    # await sync_learner(user_id, pool)
    avatar_url = await update_avatar(file, user_id, s3_session, pool)
    return UploadAvatarResponse(user_id=user_id, avatar_url=avatar_url)


@router.patch("")
async def update_infor(
    payload: LearnerUpdateRequest,
    # jwt_payload: Payload = Depends(verify_token),
    pool: asyncpg.Pool = Depends(get_postgre_pool),
) -> LearnerUpdateResponse:

    # user_id = jwt_payload["sub"]
    user_id = 1
    data = await update_learner(user_id, pool, payload)

    return LearnerUpdateResponse(
        user_id=user_id,
        name=data["name"],
        nickname=data["nickname"],
        avatar_url=data["avatar_url"],
        date_of_birth=data["date_of_birth"],
        settings=data["settings"],
    )


@router.get(
    path="",
    description="Learner gets basic information",
    response_model=GetLearnerResponse,
)
async def get_me(
    # jwt_payload: Payload = Depends(verify_token),
    learner_service: LearnerService = Depends(get_learner_service),
) -> GetLearnerResponse:
    # user_id = jwt_payload["sub"]
    user_id = 1
    learner = await learner_service.get_learner_information(user_id)
    return GetLearnerResponse(
        user_id=user_id,
        name=learner.name,
        nickname=learner.nickname,
        avatar_url=learner.avatar_url,
        date_of_birth=learner.date_of_birth,
        settings=learner.settings,
    )
