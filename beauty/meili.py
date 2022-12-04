from meilisearch_python_async import Client
from tortoise.functions import Avg

from beauty.models import Picture, Collection
from beauty.settings import settings

client = Client(url=settings.MEILI_URL, api_key=settings.MEILI_MASTER_KEY)
pictures_index = client.index("beauty-pictures")
collections_index = client.index("beauty-collections")


async def init():
    await pictures_index.update_sortable_attributes(
        sortable_attributes=["favorite_count", "avg_rating"]
    )


async def add_collections(*collections: Collection):
    data = [
        {
            "id": c.pk,
            "title": c.title,
            "description": c.description,
        }
        for c in collections
    ]
    return await collections_index.add_documents(data)


async def add_pictures(*pictures: Picture):
    data = [
        {
            "id": p.pk,
            "description": p.description,
            "favorite_count": await p.favorites.all().count(),
            "avg_rating": (
                await p.ratings.all()
                .annotate(avg_rating=Avg("rating"))
                .values("avg_rating")
            )[0]["avg_rating"]
            or 0,
        }
        for p in pictures
    ]
    return await pictures_index.add_documents(data)
