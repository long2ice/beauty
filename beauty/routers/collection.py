from fastapi import APIRouter, Depends, Query

from beauty.meili import collections_index
from beauty.models import Collection, Picture
from beauty.schemas import Page

router = APIRouter()


@router.get("")
async def get_collections(page: Page = Depends(Page)):
    return (
        await Collection.all()
        .order_by("id")
        .limit(page.limit)
        .offset(page.offset)
        .values("id", "title", "description")
    )


@router.get("/search")
async def search_collections(
    keyword: str = Query(..., max_length=10), page: Page = Depends(Page)
):
    result = await collections_index.search(
        keyword,
        limit=page.limit,
        offset=page.offset,
    )
    return result.hits


@router.get("/{pk}/pictures")
async def get_collection_pictures(pk: int):
    return await Picture.filter(collection_id=pk).values("url", "description")
