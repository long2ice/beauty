import random

from fastapi import APIRouter, Depends, Query
from meilisearch_python_async.models.search import SearchResults
from pydantic import NonNegativeInt

from beauty.depends import auth_required, get_search_filters, store_keyword
from beauty.models import Favorite, Like, Picture
from beauty.responses import PictureResponse
from beauty.schemas import Page
from beauty.third import meili
from beauty.third.meili import pictures_index
from beauty.third.redis import Key, redis

router = APIRouter()


async def handle_search_results(results: SearchResults, user_id: int, extra: bool):
    data = results.hits
    ids = [d["id"] for d in data]
    pictures = await Picture.filter(pk__in=ids).values("id", "url")
    pictures_map = {p["id"]: p for p in pictures}
    for item in data:
        item.update(pictures_map.get(item["id"]))  # type: ignore
        if extra:
            item["favorite"] = await Favorite.filter(
                user_id=user_id, picture_id=item["id"]
            ).exists()
            item["like"] = await Like.filter(
                user_id=user_id, picture_id=item["id"]
            ).exists()
    return {
        "total": results.total_hits,
        "data": data,
    }


@router.get("", response_model=PictureResponse)
async def get_pictures(
    page: Page = Depends(Page),
    extra: bool = False,
    user_id=Depends(auth_required),
    search_filters=Depends(get_search_filters),
):
    results = await pictures_index.search(
        None,
        offset=page.offset,
        limit=page.limit,
        sort=["id:desc"],
        filter=search_filters,
        attributes_to_retrieve=[
            "id",
            "favorite_count",
            "like_count",
            "description",
        ],
    )
    return await handle_search_results(results, user_id, extra)


@router.get("/keyword")
async def get_keywords(limit: NonNegativeInt = 10):
    data = await redis.zrevrangebyscore(  # type: ignore
        Key.keywords, max="+inf", min="-inf", start=0, num=limit * 10
    )
    return random.sample(data, min(len(data), limit))


@router.get("/tag", response_model=list[str])
async def get_picture_tags():
    tags = await redis.zrevrange(Key.tags, 0, -1)
    return [
        "最新",
        "热门",
    ] + list(tags)


@router.post("/{pk}/favorite")
async def favorite_picture(pk: int, user_id=Depends(auth_required)):
    _, created = await Favorite.get_or_create(user_id=user_id, picture_id=pk)
    if not created:
        await Favorite.filter(user_id=user_id, picture_id=pk).delete()
    await meili.add_pictures(
        await Picture.get(pk=pk).only("id", "description", "category", "created_at")
    )
    return {"favorite": created}


@router.post("/{pk}/like")
async def like_picture(pk: int, user_id=Depends(auth_required)):
    _, created = await Like.get_or_create(user_id=user_id, picture_id=pk)
    if not created:
        await Like.filter(user_id=user_id, picture_id=pk).delete()
    await meili.add_pictures(
        await Picture.get(pk=pk).only("id", "description", "category", "created_at")
    )
    return {"like": created}


@router.get("/hot", response_model=PictureResponse)
async def get_hot_pictures(
    page: Page = Depends(Page),
    extra: bool = False,
    user_id=Depends(auth_required),
    search_filters=Depends(get_search_filters),
):
    results = await pictures_index.search(
        "",
        limit=page.limit,
        offset=page.offset,
        filter=search_filters,
        sort=["like_count:desc"],
        attributes_to_retrieve=[
            "id",
            "favorite_count",
            "like_count",
            "description",
        ],
    )
    return await handle_search_results(results, user_id, extra)


@router.get(
    "/search",
    dependencies=[Depends(store_keyword)],
    response_model=PictureResponse,
)
async def search_pictures(
    keyword: str = Query(..., max_length=10, min_length=1),
    page: Page = Depends(Page),
    extra: bool = False,
    user_id=Depends(auth_required),
    search_filters=Depends(get_search_filters),
):
    results = await pictures_index.search(
        keyword,
        limit=page.limit,
        offset=page.offset,
        filter=search_filters,
        sort=["like_count:desc"],
        attributes_to_retrieve=[
            "id",
            "favorite_count",
            "like_count",
            "description",
        ],
    )
    return await handle_search_results(results, user_id, extra)


@router.get("/favorite", response_model=PictureResponse)
async def get_favorite_pictures(
    user_id=Depends(auth_required), page: Page = Depends(Page), extra: bool = False
):
    data = (
        await Favorite.filter(user_id=user_id)
        .select_related("picture")
        .limit(page.limit)
        .offset(page.offset)
        .values(
            id="picture__id",
            url="picture__url",
            description="picture__description",
        )
    )
    if extra:
        for picture in data:
            picture["favorite"] = True
            picture["like"] = await Like.filter(
                user_id=user_id, picture_id=picture["id"]
            ).exists()
            picture["favorite_count"] = await Favorite.filter(
                picture_id=picture["id"]
            ).count()
            picture["like_count"] = await Like.filter(picture_id=picture["id"]).count()
    return {
        "total": await Favorite.filter(user_id=user_id).count(),
        "data": data,
    }
