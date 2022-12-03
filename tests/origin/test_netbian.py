import pytest

from beauty.origin.netbian import NetBian


@pytest.fixture
async def netbian():
    netbian = NetBian()
    yield netbian
    await netbian.close()


async def test_netbian(netbian):
    page = 1
    res = await netbian.get_page(page)
    ret = await netbian.parse(res)
    assert len(ret) > 0
