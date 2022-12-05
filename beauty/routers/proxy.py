import json
from io import BytesIO

import httpx
from fastapi import APIRouter
from starlette.responses import StreamingResponse

from beauty.enums import Origin
from beauty.redis import Key, redis
from beauty.settings import settings

router = APIRouter()


@router.get("/img.netbian.com/{full_path:path}")
async def proxy_netbian(full_path: str):
    url = f"http://img.netbian.com/{full_path}"
    cookies = await redis.hget(Key.cookies, Origin.netbian.value)  # type: ignore
    if cookies:
        cookies = json.loads(cookies)
    else:
        cookies = []
    httpx_cookies = httpx.Cookies()
    for cookie in cookies:
        httpx_cookies.set(cookie["name"], cookie["value"])
    async with httpx.AsyncClient() as client:
        res = await client.get(
            url,
            cookies=httpx_cookies,
            headers={"User-Agent": settings.USER_AGENT},
        )
        headers = res.headers
        set_cookie = headers.get("set-cookie")
        if set_cookie:
            set_cookie = set_cookie.replace("netbian.com", "long2ice.com")
            headers["set-cookie"] = set_cookie
        response = StreamingResponse(
            BytesIO(res.content), media_type="image/svg+xml", headers=headers
        )
        return response
