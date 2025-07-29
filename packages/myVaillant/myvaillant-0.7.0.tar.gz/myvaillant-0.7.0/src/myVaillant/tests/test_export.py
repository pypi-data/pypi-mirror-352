import pytest as pytest

from ..export import main as export_main
from .utils import list_test_data


@pytest.mark.parametrize("test_data", list_test_data())
async def test_export(myvaillant_aioresponses, test_data) -> None:
    with myvaillant_aioresponses(test_data) as _:
        result = await export_main("test@example.com", "test", "vaillant", "germany")
        assert isinstance(result, list)


@pytest.mark.parametrize("test_data", list_test_data())
async def test_export_data(myvaillant_aioresponses, test_data) -> None:
    with myvaillant_aioresponses(test_data) as _:
        result = await export_main(
            "test@example.com", "test", "vaillant", "germany", data=True
        )
        assert isinstance(result, list)
