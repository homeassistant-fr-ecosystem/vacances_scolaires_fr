"""Tests for VacancesScolairesAPI fetch and cache logic."""

import json
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import aiohttp
import pytest

from custom_components.vacances_scolaires_fr.api import VacancesScolairesAPI

from .conftest import ACADEMY, MOCK_API_RESPONSE, ZONE


@pytest.fixture
def api_with_cache(tmp_path: Any) -> VacancesScolairesAPI:
    """Return an API instance with a real tmp cache directory."""
    return VacancesScolairesAPI(ZONE, ACADEMY, hass_config_path=str(tmp_path))


def _make_mock_response(
    status: int = 200, json_data: dict[str, Any] | None = None
) -> MagicMock:
    """Build a mock aiohttp response."""
    resp = MagicMock()
    resp.status = status
    resp.json = AsyncMock(return_value=json_data or MOCK_API_RESPONSE)
    resp.text = AsyncMock(return_value="error body")
    resp.__aenter__ = AsyncMock(return_value=resp)
    resp.__aexit__ = AsyncMock(return_value=False)
    return resp


def _mock_session(resp: MagicMock) -> MagicMock:
    """Build a mock aiohttp.ClientSession whose .get() returns resp."""
    session = MagicMock()
    session.get = MagicMock(return_value=resp)
    session.__aenter__ = AsyncMock(return_value=session)
    session.__aexit__ = AsyncMock(return_value=False)
    return session


class TestAsyncFetchVacances:
    async def test_fetches_from_api_when_no_cache(
        self, api_with_cache: VacancesScolairesAPI
    ) -> None:
        resp = _make_mock_response(200, MOCK_API_RESPONSE)
        session = _mock_session(resp)

        with patch("aiohttp.ClientSession", return_value=session):
            result = await api_with_cache.async_fetch_vacances()

        assert result is True
        assert len(api_with_cache._vacances) == 3

    async def test_returns_false_on_api_error(
        self, api_with_cache: VacancesScolairesAPI
    ) -> None:
        resp = _make_mock_response(500)
        session = _mock_session(resp)

        with patch("aiohttp.ClientSession", return_value=session):
            result = await api_with_cache.async_fetch_vacances()

        assert result is False
        assert api_with_cache._use_static_data is True

    async def test_returns_false_on_connection_error(
        self, api_with_cache: VacancesScolairesAPI
    ) -> None:
        session = MagicMock()
        session.get = MagicMock(side_effect=aiohttp.ClientError("connection failed"))
        session.__aenter__ = AsyncMock(return_value=session)
        session.__aexit__ = AsyncMock(return_value=False)

        with patch("aiohttp.ClientSession", return_value=session):
            result = await api_with_cache.async_fetch_vacances()

        assert result is False

    async def test_uses_cache_when_valid(
        self, api_with_cache: VacancesScolairesAPI
    ) -> None:
        # Write a valid cache file
        cache_path = api_with_cache._get_cache_path()
        assert cache_path is not None
        import os

        os.makedirs(api_with_cache._cache_dir, exist_ok=True)  # type: ignore[arg-type]
        with open(cache_path, "w") as f:
            json.dump(MOCK_API_RESPONSE, f)

        with patch.object(
            api_with_cache, "_is_cache_valid", AsyncMock(return_value=True)
        ):
            with patch("aiohttp.ClientSession") as mock_session_cls:
                result = await api_with_cache.async_fetch_vacances()
                mock_session_cls.assert_not_called()

        assert result is True
        assert len(api_with_cache._vacances) == 3

    async def test_falls_back_to_old_cache_on_api_error(
        self, api_with_cache: VacancesScolairesAPI
    ) -> None:
        # Write a stale cache file
        import os

        os.makedirs(api_with_cache._cache_dir, exist_ok=True)  # type: ignore[arg-type]
        cache_path = api_with_cache._get_cache_path()
        assert cache_path is not None
        with open(cache_path, "w") as f:
            json.dump(MOCK_API_RESPONSE, f)

        session = MagicMock()
        session.get = MagicMock(side_effect=aiohttp.ClientError("timeout"))
        session.__aenter__ = AsyncMock(return_value=session)
        session.__aexit__ = AsyncMock(return_value=False)

        with patch("aiohttp.ClientSession", return_value=session):
            result = await api_with_cache.async_fetch_vacances()

        assert result is True
        assert len(api_with_cache._vacances) == 3

    async def test_saves_response_to_cache(
        self, api_with_cache: VacancesScolairesAPI
    ) -> None:
        resp = _make_mock_response(200, MOCK_API_RESPONSE)
        session = _mock_session(resp)

        with patch("aiohttp.ClientSession", return_value=session):
            await api_with_cache.async_fetch_vacances()

        cache_path = api_with_cache._get_cache_path()
        assert cache_path is not None
        import os

        assert os.path.exists(cache_path)
        with open(cache_path) as f:
            cached = json.load(f)
        assert cached == MOCK_API_RESPONSE


class TestCacheManagement:
    async def test_clear_cache_removes_file(
        self, api_with_cache: VacancesScolairesAPI
    ) -> None:
        import os

        os.makedirs(api_with_cache._cache_dir, exist_ok=True)  # type: ignore[arg-type]
        cache_path = api_with_cache._get_cache_path()
        assert cache_path is not None
        with open(cache_path, "w") as f:
            f.write("{}")

        await api_with_cache.async_clear_cache()
        assert not os.path.exists(cache_path)

    async def test_clear_cache_noop_when_no_file(
        self, api_with_cache: VacancesScolairesAPI
    ) -> None:
        # Should not raise even if file doesn't exist
        await api_with_cache.async_clear_cache()

    async def test_clear_cache_noop_when_no_cache_dir(
        self, api: VacancesScolairesAPI
    ) -> None:
        # api fixture has no cache dir
        await api.async_clear_cache()

    def test_is_cache_valid_returns_false_when_no_path(
        self, api: VacancesScolairesAPI
    ) -> None:
        assert api._is_cache_valid_sync() is False

    def test_is_cache_valid_returns_false_when_file_missing(
        self, api_with_cache: VacancesScolairesAPI
    ) -> None:
        assert api_with_cache._is_cache_valid_sync() is False

    def test_is_cache_valid_returns_true_for_fresh_file(
        self, api_with_cache: VacancesScolairesAPI
    ) -> None:
        import os

        os.makedirs(api_with_cache._cache_dir, exist_ok=True)  # type: ignore[arg-type]
        cache_path = api_with_cache._get_cache_path()
        assert cache_path is not None
        with open(cache_path, "w") as f:
            f.write("{}")

        assert api_with_cache._is_cache_valid_sync() is True

    def test_get_cache_path_no_path_traversal(self) -> None:
        # Academy names with slashes or dots should be sanitized
        api = VacancesScolairesAPI("A", "Besançon", hass_config_path="/tmp")
        path = api._get_cache_path()
        assert path is not None
        filename = path.split("/")[-1]
        assert "/" not in filename
        assert ".." not in filename
        assert filename.startswith("vacances_")
        assert filename.endswith(".json")
