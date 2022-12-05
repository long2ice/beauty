import asyncio
import json

import requests_html
from playwright.async_api import async_playwright

from beauty.enums import Origin
from beauty.models import Picture
from beauty.origin import OriginBase
from beauty.redis import Key, redis
from beauty.settings import settings


class NetBian(OriginBase):
    homepage = "http://www.netbian.com"
    origin = Origin.netbian

    def get_page_url(self, page: int) -> str:
        if page == 1:
            return f"{self.homepage}/shouji/meinv/index.html"
        else:
            return f"{self.homepage}/shouji/meinv/index_{page}.html"

    async def request(self, url: str):
        res = await super().request(url)
        if res.status_code == 200:
            return res
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            context = await browser.new_context(user_agent=settings.USER_AGENT)
            page = await context.new_page()
            await page.goto(url)
            await page.reload()
            await asyncio.sleep(5)
            content = await page.content()
            cookies = await context.cookies()
            await redis.hset(Key.cookies, self.origin.value, json.dumps(cookies))  # type: ignore
            for cookie in cookies:
                self.asession.cookies.set(
                    cookie["name"],
                    cookie["value"],
                )
            html = requests_html.HTML(
                url=url,
                html=content.encode("gbk"),
                default_encoding="gbk",
            )
            res.html.__dict__.update(html.__dict__)
        return res

    async def parse(self, res: requests_html.HTMLResponse) -> list[Picture]:
        pics = []
        for li in res.html.find(".list ul li"):
            if li.attrs.get("class") == "nextpage":
                continue
            img = li.find("a img", first=True)
            if not img:
                continue
            src = img.attrs.get("src")
            alt = img.attrs.get("alt")
            src = src.replace("small", "")
            src = src.split(".jpg")[0][:-10] + ".jpg"
            src = src.replace(
                "http://img.netbian.com", settings.SITE_URL + "/img.netbian.com"
            )
            pics.append(
                Picture(
                    origin=Origin.netbian,
                    url=src,
                    description=alt,
                )
            )
        return pics
