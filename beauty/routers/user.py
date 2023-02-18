import hashlib
from typing import Optional

from fastapi import APIRouter, Depends, UploadFile
from pydantic import BaseModel

from beauty import constants, responses
from beauty.depends import get_current_user
from beauty.third import s3

router = APIRouter()


class UserUpdate(BaseModel):
    nickname: Optional[str]


@router.post("/avatar", response_model=responses.User)
async def update_avatar(
    avatar: UploadFile,
    user=Depends(get_current_user),
):
    filename = hashlib.md5(user.openid.encode()).hexdigest()
    filename = f'{constants.AVATAR}/{filename}.{avatar.filename.split(".")[-1]}'  # type:ignore
    await s3.upload_file(
        filename, avatar.content_type, await avatar.read()  # type:ignore
    )
    user.avatar = filename
    await user.save(update_fields=["avatar"])
    return user


@router.put("", response_model=responses.User)
async def update_user(
    body: UserUpdate,
    user=Depends(get_current_user),
):
    if body.nickname:
        user.nickname = body.nickname
        await user.save(update_fields=["nickname"])
    return user


@router.get("", response_model=responses.User)
async def get_user(user=Depends(get_current_user)):
    return user
