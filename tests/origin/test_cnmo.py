import pytest

from beauty.origin.cnmo import Cnmo


@pytest.fixture
async def cnmo():
    cnmo = Cnmo()
    yield cnmo
    await cnmo.close()


async def test_cnmo(cnmo):
    page = 1
    res = await cnmo.get_page(page)
    ret = await cnmo.parse(res)
    assert len(ret) > 0
