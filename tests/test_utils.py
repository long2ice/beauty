import asyncio

from beauty.enums import Origin
from beauty.models import Picture
from beauty.tasks import download_and_upload


async def test_download_and_upload():
    picture = await Picture.filter(url=None, origin=Origin.win3000).only("id", "origin_url").first()
    sem = asyncio.Semaphore(10)
    ret = await download_and_upload(sem, picture.pk, Origin.netbian, picture.origin_url)
    assert ret
