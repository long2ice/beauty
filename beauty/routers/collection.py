from fastapi import APIRouter, Depends, Query

from beauty.depends import auth_required, get_search_filters
from beauty.models import Collection, Favorite, Like, Picture
from beauty.responses import CollectionResponse
from beauty.responses import Picture as PictureModel
from beauty.schemas import Page
from beauty.third.meili import collections_index

router = APIRouter()


@router.get("/search", response_model=CollectionResponse)
async def search_collections(
    keyword: str = Query(..., max_length=10),
    page: Page = Depends(Page),
    search_filters=Depends(get_search_filters),
):
    result = await collections_index.search(
        keyword,
        limit=page.limit,
        offset=page.offset,
        sort=["id:desc"],
        filter=search_filters,
    )
    data = result.hits
    for collection in data:
        picture = await Picture.filter(collection_id=collection["id"]).only("url").first()
        if not picture:
            await Collection.filter(id=collection["id"]).delete()
            continue
        collection["url"] = picture.url
    return {
        "total": result.estimated_total_hits,
        "data": data,
    }


@router.get("/{pk}/picture", response_model=list[PictureModel])
async def get_collection_pictures(pk: int, user_id=Depends(auth_required)):
    data = await Picture.filter(collection_id=pk).values("id", "url", "description")
    for picture in data:
        picture["like"] = await Like.filter(user_id=user_id, picture_id=picture["id"]).exists()
        picture["favorite"] = await Favorite.filter(
            user_id=user_id, picture_id=picture["id"]
        ).exists()
        picture["like_count"] = await Like.filter(picture_id=picture["id"]).count()
        picture["favorite_count"] = await Favorite.filter(picture_id=picture["id"]).count()
    return data
