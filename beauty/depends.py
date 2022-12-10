import datetime
import hashlib
import time
from json import JSONDecodeError
from typing import Dict

import jwt
from cachetools import TTLCache
from fastapi import Depends, Header, HTTPException, Query
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import constr
from starlette.requests import Request
from starlette.status import HTTP_401_UNAUTHORIZED, HTTP_403_FORBIDDEN

from beauty.enums import PictureCategory
from beauty.models import User
from beauty.settings import JWT_ALGORITHM, settings
from beauty.third.redis import Key, redis

nonce_cache: TTLCache = TTLCache(maxsize=3600, ttl=int(datetime.timedelta(hours=1).total_seconds()))


def get_sign(data: Dict, timestamp: int, nonce: str):
    kvs = [f"timestamp={timestamp}", f"nonce={nonce}"]
    for key, value in data.items():
        if value is None:
            continue
        value_str = str(value)
        kvs.append(f"{key}={value_str}")
    to_encode_str = "&".join(sorted(kvs))
    to_encode_str = f"{to_encode_str}&key={settings.API_SECRET}"
    m = hashlib.md5()
    m.update(to_encode_str.encode())
    return m.hexdigest().upper()


async def sign_required(
    request: Request,
    x_sign: str = Header(..., example="sign"),
    x_nonce: constr(curtail_length=8) = Header(..., example="11111111"),  # type:ignore
    x_timestamp: int = Header(..., example=int(time.time())),
):
    if settings.DEBUG:
        return
    if request.url.path in ["/docs", "/openapi.json"]:
        return
    if request.method in ["GET", "DELETE"]:
        data = dict(request.query_params)
    else:
        try:
            data = await request.json()
        except (JSONDecodeError, UnicodeDecodeError):
            data = {}
    now = int(datetime.datetime.now().timestamp())
    if abs(now - x_timestamp) > 60 * 10:
        raise HTTPException(detail="Timestamp expired", status_code=HTTP_403_FORBIDDEN)
    if x_nonce in nonce_cache:
        raise HTTPException(detail="Nonce str repeated", status_code=HTTP_403_FORBIDDEN)
    nonce_cache[x_nonce] = True
    verified = get_sign(data, x_timestamp, x_nonce) == x_sign
    if not verified:
        raise HTTPException(detail="Signature verify failed", status_code=HTTP_403_FORBIDDEN)


async def store_keyword(
    keyword: str = Query(..., example="美女", min_length=1, max_length=10),
):
    await redis.zincrby(  # type:ignore
        Key.keywords,
        1,
        keyword,
    )


auth_scheme = HTTPBearer()


async def auth_required(token: HTTPAuthorizationCredentials = Depends(auth_scheme)):
    invalid_token = HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail="Invalid token")
    try:
        data = jwt.decode(token.credentials, settings.SECRET, algorithms=[JWT_ALGORITHM])
    except jwt.DecodeError:
        raise invalid_token
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail="Token expired")
    user_id = data.get("user_id")
    if not user_id:
        raise invalid_token
    return user_id


async def get_current_user(user_id=Depends(auth_required)):
    user = await User.get_or_none(pk=user_id)
    if not user:
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail="User not found")
    return user


def get_search_filters():
    if settings.is_auditing:
        return f"category != {PictureCategory.beauty.value}"
    return f"category = {PictureCategory.beauty.value}"
