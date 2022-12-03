from meilisearch_python_async import Client
from tortoise.functions import Avg

from beauty.models import Picture
from beauty.settings import settings

client = Client(url=settings.MEILI_URL, api_key=settings.MEILI_MASTER_KEY)
index = client.index("beauty")


async def init():
    await index.update_sortable_attributes(sortable_attributes=["favorite_count", "avg_rating"])


async def add_pictures(*pictures: Picture):
    data = [
        {
            "id": p.pk,
            "description": p.description,
            "favorite_count": await p.favorites.all().count(),
            "avg_rating": (
                await p.ratings.all().annotate(avg_rating=Avg("rating")).values("avg_rating")
            )[0]["avg_rating"]
            or 0,
        }
        for p in pictures
    ]
    return await index.add_documents(data)
