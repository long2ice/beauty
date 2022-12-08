from typing import Optional

from pydantic import BaseModel
from wechatpy import WeChatClient
from wechatpy.client.api import WeChatWxa

from beauty.exceptions import Code2SessionError
from beauty.settings import settings
from beauty.utils import run_async

client = WeChatClient(settings.WECHAT_APP_ID, settings.WECHAT_APP_SECRET)
wxa = WeChatWxa(client)


class Session(BaseModel):
    openid: Optional[str]
    session_key: Optional[str]
    unionid: Optional[str]
    errcode: Optional[int]
    errmsg: Optional[str]


async def code_to_session(code: str):
    data = await run_async(wxa.code_to_session, code)
    session = Session.parse_obj(data)
    if session.errcode is not None and session.errmsg is not None:
        raise Code2SessionError(session.errcode, session.errmsg)
    return session


async def get_user_info(openid: str):
    user = await run_async(client.user.get_user_info, openid)
    return user
