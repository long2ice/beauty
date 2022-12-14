import jwt
from fastapi import APIRouter
from pydantic import BaseModel
from tortoise.exceptions import DoesNotExist

from beauty import responses
from beauty.models import User
from beauty.settings import JWT_ALGORITHM, settings
from beauty.third.wechat import code_to_session

router = APIRouter()


class LoginBody(BaseModel):
    code: str


@router.post("/login", response_model=responses.LoginResponse)
async def login(body: LoginBody):
    session = await code_to_session(body.code)
    try:
        user = await User.get(openid=session.openid)
    except DoesNotExist:
        user = await User.create(
            openid=session.openid,
        )
    token = jwt.encode({"user_id": user.pk}, settings.SECRET, algorithm=JWT_ALGORITHM)
    return responses.LoginResponse(token=token, user=user)
