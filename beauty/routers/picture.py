import random
from typing import List, Dict

from fastapi import APIRouter, Query, Depends
from pydantic import NonPositiveInt

from beauty.depends import store_keyword, auth_required
from beauty.meili import pictures_index
from beauty.models import Picture, Favorite
from beauty.redis import redis, Key
from beauty.schemas import Page

router = APIRouter()


async def add_favorite(pictures: List[Dict], user_id: int):
    for picture in pictures:
        picture["favorite"] = await Favorite.filter(
            user_id=user_id, picture_id=picture["id"]
        ).exists()
    return pictures


@router.get(
    "",
)
async def get_pictures(
    page: Page = Depends(Page), favorite: bool = False, user=Depends(auth_required)
):
    data = (
        await Picture.all()
        .order_by("-id")
        .limit(page.limit)
        .offset(page.offset)
        .values(
            "id",
            "url",
        )
    )
    if favorite:
        data = await add_favorite(data, user.id)
    return data


@router.get("/keyword")
async def get_keywords(limit: NonPositiveInt = 10):
    data = await redis.zrevrangebyscore(
        Key.keywords, max="+inf", min="-inf", start=0, num=limit * 10
    )
    return random.sample(data, min(len(data), limit))


@router.get("/tag")
async def get_picture_tags():
    return ["最新", "热门", "小姐姐"]


@router.post("/{pk}/favorite")
async def favorite_picture(pk: int, user=Depends(auth_required)):
    _, created = await Favorite.get_or_create(user_id=user.pk, picture_id=pk)
    if not created:
        await Favorite.filter(user_id=user.pk, picture_id=pk).delete()


@router.get("/hot")
async def get_hot_pictures(
    page: Page = Depends(Page), favorite: bool = False, user=Depends(auth_required)
):
    result = await pictures_index.search(
        "",
        limit=page.limit,
        offset=page.offset,
        sort=["favorite_count:desc"],
        attributes_to_retrieve=["id"],
    )
    ids = [hit["id"] for hit in result.hits]
    data = await Picture.filter(id__in=ids).values(
        "id",
        "url",
    )
    if favorite:
        data = await add_favorite(data, user.id)
    return data


@router.get("/search", dependencies=[Depends(store_keyword)])
async def search_pictures(
    keyword: str = Query(..., max_length=10, min_length=1),
    page: Page = Depends(Page),
    favorite: bool = False,
    user=Depends(auth_required),
):
    result = await pictures_index.search(
        keyword,
        limit=page.limit,
        offset=page.offset,
        sort=["favorite_count:desc"],
    )
    ids = [hit["id"] for hit in result.hits]
    data = await Picture.filter(id__in=ids).values(
        "id",
        "url",
    )
    if favorite:
        data = await add_favorite(data, user.id)
    return data
