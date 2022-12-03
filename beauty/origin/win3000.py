import asyncio
import itertools

import requests_html
from tenacity import retry, stop_after_attempt, wait_fixed

from beauty.enums import Origin
from beauty.models import Collection, Picture
from beauty.origin import OriginBase


class Win3000(OriginBase):
    homepage = "https://www.win3000.com"
    origin = Origin.win3000

    def get_page_url(self, page: int) -> str:
        return f"{self.homepage}/mbizhi/mn/p{page}/"

    @retry(reraise=True, stop=stop_after_attempt(3), wait=wait_fixed(1))
    async def _create_collection(self, title: str, describe: str) -> Collection:
        collection, _ = await Collection.update_or_create(
            title=title,
            origin=self.origin,
            defaults=dict(
                description=describe,
            ),
        )
        return collection

    async def _get_pics(self, href: str, title: str):
        session = requests_html.AsyncHTMLSession()
        r = await session.get(href)
        await session.close()
        describe = r.html.find(".describe", first=True).text.split("作品标签")[0].strip()
        collection = await self._create_collection(title, describe)
        works_tag = r.html.find(".works-tag", first=True).text.split("上一组")[0].strip()
        pics = []
        for img in r.html.find(".bd ul li a img"):
            url = img.attrs["data-src"]
            url = url.split("_c_")[0] + ".jpg"
            pics.append(
                Picture(
                    origin=self.origin,
                    url=url,
                    description=works_tag,
                    collection=collection,
                )
            )
        return pics

    async def parse(self, res: requests_html.HTMLResponse) -> list[Picture]:
        tasks = []
        for li in res.html.find(".mobilesize li"):
            a = li.find("a", first=True)
            href = a.attrs["href"]
            title = li.find("h3", first=True).text
            tasks.append(self._get_pics(href, title))
        ret = await asyncio.gather(*tasks)
        return list(itertools.chain(*ret))
