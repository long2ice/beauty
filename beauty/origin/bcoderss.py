import requests_html
from loguru import logger

from beauty.enums import Origin
from beauty.models import Picture
from beauty.origin import OriginBase


class Bcoderss(OriginBase):
    homepage = "https://m.bcoderss.com/tag/美女/"
    origin = Origin.bcoderss

    def get_page_url(self, page: int) -> str:
        if page == 1:
            return self.homepage
        else:
            return f"{self.homepage}page/{page}/"

    async def parse(self, res: requests_html.HTMLResponse) -> list[Picture]:
        pics = []
        for img in res.html.find(".wallpaper li a img"):
            try:
                title = img.attrs["title"]
                src = img.attrs["src"]
                last_index = src.rfind("-")
                origin_url = src[:last_index] + ".jpg"
                pic = Picture(
                    origin=self.origin,
                    origin_url=origin_url,
                    description=title,
                )
                pics.append(pic)
            except Exception as e:
                logger.error(f"bcoderss parse error: {e}")
        return pics
