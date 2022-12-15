import json
import re

import requests_html
from tortoise.exceptions import IntegrityError

from beauty.enums import Origin
from beauty.models import Collection, Picture
from beauty.origin import OriginBase


class Cnmo(OriginBase):
    homepage = "https://m.cnmo.com/app/wallpaper/s152/"
    origin = Origin.cnmo

    def is_stop(self, res: requests_html.HTMLResponse) -> bool:
        content = self._parse_content(res.text)
        return content.get("status") == -1

    @classmethod
    def _parse_content(cls, content: str):
        ret = re.findall(r"getData\((.*)\)", content)
        return json.loads(ret[0])

    def get_page_url(self, page: int) -> str:
        return (
            f"https://m.cnmo.com/app/index.php?c=Wallpaper&"
            f"m=AjaxGetInfoList&callback=getData&subclassid=152&page={page}"
        )

    async def _create_collection(self, name: str) -> Collection:
        try:
            collection = await Collection.create(
                title=name,
                origin=self.origin,
                description=name,
            )
        except IntegrityError:
            collection = await Collection.get(title=name, origin=self.origin)
            collection.description = name
            await collection.save(update_fields=["description"])
        return collection

    async def parse(self, res: requests_html.HTMLResponse) -> list[Picture]:
        content = self._parse_content(res.text)
        data = content.get("data")
        pics = []
        for item in data:
            cover_pic = item.get("cover_pic").replace("middle", "big")
            pic_num = int(item.get("pic_num"))
            name = item.get("name")
            collection = await self._create_collection(name)
            last_index = cover_pic.rfind("/")
            index = int(cover_pic.split("/")[-1].split(".")[0])
            for i in range(0, pic_num):
                pic = Picture(
                    origin=self.origin,
                    origin_url=cover_pic[:last_index] + f"/{index + i}.jpg",
                    description=name,
                    collection=collection,
                )
                pics.append(pic)
        return pics
