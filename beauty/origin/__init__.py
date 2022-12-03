import abc
import asyncio

import requests_html

from beauty.enums import Origin
from beauty.models import Picture


class OriginBase:
    homepage: str
    sem_value: int = 10
    sem: asyncio.Semaphore
    origin: Origin

    def __init__(self):
        self.asession = requests_html.AsyncHTMLSession(
            browser_args={
                "args": ["--no-sandbox"],
            }
        )
        self.sem = asyncio.Semaphore(self.sem_value)

    @abc.abstractmethod
    def get_page_url(self, page: int) -> str:
        raise NotImplementedError

    def is_stop(self, res: requests_html.HTMLResponse) -> bool:
        return res.status_code == 404

    async def request(self, url: str) -> requests_html.HTMLResponse:
        return await self.asession.get(url)

    async def request_with_sem(self, url: str):
        async with self.sem:
            return await self.request(url)

    async def get_page(self, page: int):
        url = self.get_page_url(page)
        res = await self.request_with_sem(url)
        return res

    async def close(self):
        await self.asession.close()

    @abc.abstractmethod
    async def parse(self, res: requests_html.HTMLResponse) -> list[Picture]:
        raise NotImplementedError

    async def run(self):
        page = 1
        while True:
            res = await self.get_page(page)
            is_stop = self.is_stop(res)
            if is_stop:
                break
            yield await self.parse(res)
            page += 1
