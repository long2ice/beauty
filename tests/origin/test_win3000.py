import pytest

from beauty.origin.win3000 import Win3000MN


@pytest.fixture
async def win3000():
    win3000 = Win3000MN()
    yield win3000
    await win3000.close()


async def test_win3000(win3000):
    page = 1
    res = await win3000.get_page(page)
    ret = await win3000.parse(res)
    assert len(ret) > 0
