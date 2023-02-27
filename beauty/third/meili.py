from meilisearch_python_async import Client

from beauty.models import Picture
from beauty.settings import settings

client = Client(url=settings.MEILI_URL, api_key=settings.MEILI_MASTER_KEY)
pictures_index = client.index("beauty-pictures")
collections_index = client.index("beauty-collections")


async def init():
    await pictures_index.update_sortable_attributes(
        sortable_attributes=["id", "favorite_count", "like_count"]
    )
    await pictures_index.update_filterable_attributes(
        [
            "category",
        ]
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
    await collections_index.update_sortable_attributes(sortable_attributes=["id"])
    await collections_index.update_ranking_rules(
        [
            "sort",
            "words",
            "typo",
            "proximity",
            "attribute",
            "exactness",
        ]
    )
    await collections_index.update_filterable_attributes(
        [
            "category",
        ]
    )


async def update_pictures(*pictures: Picture):
    data = [
        {
            "id": p.pk,
            "description": p.description,
            "favorite_count": await p.favorites.all().count(),
            "like_count": await p.likes.all().count(),
            "category": p.category,
        }
        for p in pictures
    ]
    return await pictures_index.update_documents(data)
