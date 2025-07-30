from __future__ import annotations

import os
import logging
from typing import TYPE_CHECKING, Iterator, AsyncIterator

import pytest
from pytest_asyncio import is_async_test

from dinari_api_sdk import Dinari, AsyncDinari

if TYPE_CHECKING:
    from _pytest.fixtures import FixtureRequest  # pyright: ignore[reportPrivateImportUsage]

pytest.register_assert_rewrite("tests.utils")

logging.getLogger("dinari_api_sdk").setLevel(logging.DEBUG)


# automatically add `pytest.mark.asyncio()` to all of our async tests
# so we don't have to add that boilerplate everywhere
def pytest_collection_modifyitems(items: list[pytest.Function]) -> None:
    pytest_asyncio_tests = (item for item in items if is_async_test(item))
    session_scope_marker = pytest.mark.asyncio(loop_scope="session")
    for async_test in pytest_asyncio_tests:
        async_test.add_marker(session_scope_marker, append=False)


base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")

api_key_id = "My API Key ID"
api_secret_key = "My API Secret Key"


@pytest.fixture(scope="session")
def client(request: FixtureRequest) -> Iterator[Dinari]:
    strict = getattr(request, "param", True)
    if not isinstance(strict, bool):
        raise TypeError(f"Unexpected fixture parameter type {type(strict)}, expected {bool}")

    with Dinari(
        base_url=base_url, api_key_id=api_key_id, api_secret_key=api_secret_key, _strict_response_validation=strict
    ) as client:
        yield client


@pytest.fixture(scope="session")
async def async_client(request: FixtureRequest) -> AsyncIterator[AsyncDinari]:
    strict = getattr(request, "param", True)
    if not isinstance(strict, bool):
        raise TypeError(f"Unexpected fixture parameter type {type(strict)}, expected {bool}")

    async with AsyncDinari(
        base_url=base_url, api_key_id=api_key_id, api_secret_key=api_secret_key, _strict_response_validation=strict
    ) as client:
        yield client
