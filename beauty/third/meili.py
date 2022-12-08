from meilisearch_python_async import Client

from beauty.models import Collection, Picture
from beauty.settings import settings

client = Client(url=settings.MEILI_URL, api_key=settings.MEILI_MASTER_KEY)
pictures_index = client.index("beauty-pictures")
collections_index = client.index("beauty-collections")


async def init():
    await pictures_index.update_sortable_attributes(
        sortable_attributes=["id", "favorite_count", "like_count"]
    )
    await pictures_index.update_ranking_rules(
        [
            "sort",
            "words",
            "typo",
            "proximity",
            "attribute",
            "exactness",
        ]
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
            "like_count": await p.likes.all().count(),
        }
        for p in pictures
    ]
    return await pictures_index.add_documents(data)


async def delete_pictures(*pk: int):
    return await pictures_index.delete_documents([str(p) for p in pk])
