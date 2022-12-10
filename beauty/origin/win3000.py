import asyncio
import itertools

import requests_html
from bs4 import BeautifulSoup
from tortoise.exceptions import IntegrityError

from beauty.enums import Origin, PictureCategory
from beauty.models import Collection, Picture
from beauty.origin import OriginBase


class Win3000MN(OriginBase):
    homepage = "https://www.win3000.com"
    origin = Origin.win3000
    category = PictureCategory.beauty

    def get_page_url(self, page: int) -> str:
        return f"{self.homepage}/mbizhi/mn/p{page}/"

    async def _create_collection(self, title: str, describe: str) -> Collection:
        try:
            collection = await Collection.create(
                title=title,
                origin=self.origin,
                description=describe,
                category=self.category,
            )
        except IntegrityError:
            collection = await Collection.get(title=title, origin=self.origin)
            collection.description = describe
            collection.category = self.category
            await collection.save(update_fields=["description", "category"])
        return collection

    async def _get_pics(self, href: str, title: str):
        session = requests_html.AsyncHTMLSession()
        r = await session.get(href)
        await session.close()
        describe = r.html.find(".describe", first=True).text.split("作品标签")[0].strip()
        collection = await self._create_collection(title, describe)
        works_tag = r.html.find(".works-tag", first=True).text
        works_tag = works_tag.split("上一组")[0].strip()
        works_tag = works_tag.split("下一组")[0].strip()
        pics = []
        for img in r.html.find(".bd ul li a img"):
            url = img.attrs["data-src"]
            url = url.split("_c_")[0] + ".jpg"
            pics.append(
                Picture(
                    origin=self.origin,
                    origin_url=url,
                    description=works_tag,
                    collection=collection,
                    category=self.category,
                )
            )
        return pics

    async def parse(self, res: requests_html.HTMLResponse) -> list[Picture]:
        tasks = []
        bs = BeautifulSoup(res.html.html, "lxml")
        mobilesize = bs.find(class_="mobilesize")
        for li in mobilesize.find_all("li"):
            a = li.find("a")
            href = a.attrs["href"]
            title = li.find("h3").text
            tasks.append(self._get_pics(href, title))
        ret = await asyncio.gather(*tasks)
        return list(itertools.chain(*ret))


class Win3000FJ(Win3000MN):
    category = PictureCategory.scenery

    def get_page_url(self, page: int) -> str:
        return f"{self.homepage}/mbizhi/fj/p{page}/"
