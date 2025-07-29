import pytest

from myVaillant.api import MyVaillantAPI
from myVaillant.tests.utils import _mocked_api, _myvaillant_aioresponses


@pytest.fixture
def myvaillant_aioresponses():
    return _myvaillant_aioresponses()


@pytest.fixture
async def mocked_api() -> MyVaillantAPI:
    return await _mocked_api()
