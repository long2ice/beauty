import hashlib
import os.path
from typing import Optional

import aiofiles
from fastapi import APIRouter, Depends, UploadFile
from pydantic import BaseModel

from beauty import constants, responses
from beauty.depends import get_current_user

router = APIRouter()


class UserUpdate(BaseModel):
    nickname: Optional[str]


@router.post("/avatar", response_model=responses.User)
async def update_avatar(
    avatar: UploadFile,
    user=Depends(get_current_user),
):
    filename = hashlib.md5(user.openid.encode()).hexdigest()
    filename = f'{filename}.{avatar.filename.split(".")[-1]}'
    async with aiofiles.open(os.path.join(constants.AVATAR_DIR, filename), "wb") as f:
        await f.write(await avatar.read())
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
