import pytest

from beauty.origin.bcoderss import Bcoderss


@pytest.fixture
async def bcoderss():
    bcoderss = Bcoderss()
    yield bcoderss
    await bcoderss.close()


async def test_bcoderss(bcoderss):
    page = 1
    res = await bcoderss.get_page(page)
    ret = await bcoderss.parse(res)
    assert len(ret) > 0
