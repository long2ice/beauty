import random

from fastapi import APIRouter, Depends, Query
from meilisearch_python_async.models.search import SearchResults
from pydantic import NonNegativeInt

from beauty.depends import auth_required, store_keyword
from beauty.meili import pictures_index
from beauty.models import Favorite, Like, Picture
from beauty.redis import Key, redis
from beauty.responses import PictureResponse
from beauty.schemas import Page

router = APIRouter()


async def handle_search_results(results: SearchResults, user_id: int, extra: bool):
    results_map = {x.get("id"): x for x in results.hits}
    pictures = await Picture.filter(pk__in=results_map.keys()).values("id", "url")

    for picture in pictures:
        picture.update(results_map.get(picture["id"]))  # type: ignore
        if extra:
            picture["favorite"] = await Favorite.filter(
                user_id=user_id, picture_id=picture["id"]
            ).exists()
            picture["like"] = await Like.filter(user_id=user_id, picture_id=picture["id"]).exists()
    return {
        "total": results.estimated_total_hits,
        "data": pictures,
    }


@router.get("", response_model=PictureResponse)
async def get_pictures(
    page: Page = Depends(Page), extra: bool = False, user=Depends(auth_required)
):
    results = await pictures_index.search(
        "",
        limit=page.limit,
        offset=page.offset,
        attributes_to_retrieve=[
            "id",
            "favorite_count",
            "like_count",
        ],
    )
    return await handle_search_results(results, user.id, extra)


@router.get("/keyword")
async def get_keywords(limit: NonNegativeInt = 10):
    data = await redis.zrevrangebyscore(  # type: ignore
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
    return {"favorite": created}


@router.post("/{pk}/like")
async def like_picture(pk: int, user=Depends(auth_required)):
    _, created = await Like.get_or_create(user_id=user.pk, picture_id=pk)
    if not created:
        await Like.filter(user_id=user.pk, picture_id=pk).delete()
    return {"like": created}


@router.get("/hot", response_model=PictureResponse)
async def get_hot_pictures(
    page: Page = Depends(Page), extra: bool = False, user=Depends(auth_required)
):
    results = await pictures_index.search(
        "",
        limit=page.limit,
        offset=page.offset,
        sort=["like_count:desc"],
        attributes_to_retrieve=[
            "id",
            "favorite_count",
            "like_count",
        ],
    )
    return await handle_search_results(results, user.id, extra)


@router.get(
    "/search",
    dependencies=[Depends(store_keyword)],
    response_model=PictureResponse,
)
async def search_pictures(
    keyword: str = Query(..., max_length=10, min_length=1),
    page: Page = Depends(Page),
    extra: bool = False,
    user=Depends(auth_required),
):
    results = await pictures_index.search(
        keyword,
        limit=page.limit,
        offset=page.offset,
        sort=["like_count:desc"],
        attributes_to_retrieve=[
            "id",
            "favorite_count",
            "like_count",
        ],
    )
    return await handle_search_results(results, user.id, extra)
