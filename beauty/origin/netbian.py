import asyncio
import json

import requests_html
from fake_useragent import UserAgent
from playwright.async_api import async_playwright

from beauty.enums import Origin
from beauty.models import Picture
from beauty.origin import OriginBase
from beauty.third.redis import Key, redis


class NetBian(OriginBase):
    homepage = "http://www.netbian.com"
    origin = Origin.netbian

    def get_page_url(self, page: int) -> str:
        if page == 1:
            return f"{self.homepage}/shouji/meinv/index.html"
        else:
            return f"{self.homepage}/shouji/meinv/index_{page}.html"

    @classmethod
    def is_valid_cookies(cls, cookies: list):
        for cookie in cookies:
            if cookie["name"] == "yjs_js_security_passport":
                return True
        return False

    @classmethod
    async def refresh_cookies(cls):
        picture = await Picture.filter(origin=Origin.netbian).only("origin_url").first()
        if not picture:
            return
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            user_agent = UserAgent().random
            context = await browser.new_context(user_agent=user_agent)
            page = await context.new_page()
            await page.goto(picture.origin_url)
            await page.reload()
            await asyncio.sleep(5)
            cookies = await context.cookies()
            if NetBian.is_valid_cookies(cookies):
                await redis.hset(
                    Key.cookies,
                    NetBian.origin.value,
                    json.dumps(
                        {
                            "user_agent": user_agent,
                            "cookies": cookies,
                        }
                    ),
                )
            return cookies

    async def request(self, url: str):
        res = await super().request(url)
        if res.status_code == 200:
            return res
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            user_agent = UserAgent().random
            context = await browser.new_context(user_agent=user_agent)
            page = await context.new_page()
            await page.goto(url)
            await page.reload()
            await asyncio.sleep(5)
            content = await page.content()
            cookies = await context.cookies()
            if self.is_valid_cookies(cookies):
                self.asession.headers.update({"User-Agent": user_agent})
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
            pics.append(
                Picture(
                    origin=self.origin,
                    origin_url=src,
                    description=alt,
                )
            )
        return pics
