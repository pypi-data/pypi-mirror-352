import pytest as pytest

from ..api import MyVaillantAPI
from ..sample import main
from .utils import list_test_data


@pytest.mark.parametrize("test_data", list_test_data())
async def test_sample(
    myvaillant_aioresponses, mocked_api: MyVaillantAPI, mocker, test_data
) -> None:
    with myvaillant_aioresponses(test_data) as _:
        mocker.patch("myVaillant.api.MyVaillantAPI.__aenter__", return_value=mocked_api)
        await main("test@example.com", "test", "vaillant", "germany")
        await mocked_api.aiohttp_session.close()
