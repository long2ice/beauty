from fastapi import APIRouter, Depends, Query

from beauty.depends import auth_required
from beauty.meili import collections_index
from beauty.models import Favorite, Like, Picture
from beauty.schemas import Page

router = APIRouter()


@router.get("/search")
async def search_collections(keyword: str = Query(..., max_length=10), page: Page = Depends(Page)):
    result = await collections_index.search(
        keyword,
        limit=page.limit,
        offset=page.offset,
    )
    data = result.hits
    for collection in data:
        collection["url"] = (  # type: ignore
            await Picture.filter(collection_id=collection["id"]).only("url").first()  # type: ignore
        ).url  # type: ignore
    return data


@router.get("/{pk}/pictures")
async def get_collection_pictures(pk: int, user=Depends(auth_required)):
    data = await Picture.filter(collection_id=pk).values("id", "url")
    for picture in data:
        picture["like"] = await Like.filter(user_id=user.id, picture_id=picture["id"]).exists()
        picture["favorite"] = await Favorite.filter(
            user_id=user.id, picture_id=picture["id"]
        ).exists()
        picture["like_count"] = await Like.filter(picture_id=picture["id"]).count()
        picture["favorite_count"] = await Favorite.filter(picture_id=picture["id"]).count()
    return data
