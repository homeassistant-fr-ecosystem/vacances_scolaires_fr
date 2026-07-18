"""Tests for VacancesDataUpdateCoordinator."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from homeassistant.core import HomeAssistant

from custom_components.vacances_scolaires_fr.api import VacancesScolairesAPI
from custom_components.vacances_scolaires_fr.coordinator import (
    VacancesDataUpdateCoordinator,
)

from .conftest import ACADEMY, MOCK_VACANCES, ZONE


@pytest.fixture
def mock_api() -> VacancesScolairesAPI:
    """Return a mock VacancesScolairesAPI."""
    api = MagicMock(spec=VacancesScolairesAPI)
    api.get_vacances_en_cours = MagicMock(return_value=None)
    api.get_prochaines_vacances = MagicMock(return_value=None)
    api.get_jours_avant_vacances = MagicMock(return_value=None)
    api.get_jours_restants_vacances = MagicMock(return_value=None)
    api.async_fetch_vacances = AsyncMock(return_value=True)
    return api


@pytest.fixture
def mock_entry() -> MagicMock:
    """Return a mock config entry."""
    entry = MagicMock()
    entry.data = {
        "zone": ZONE,
        "academy": ACADEMY,
        "update_interval": 7,
        "verify_ssl": True,
        "timezone": "Europe/Paris",
    }
    entry.options = {}
    return entry


class TestCoordinatorInit:
    async def test_creates_api_with_zone_and_academy(
        self, hass: HomeAssistant, mock_entry: MagicMock
    ) -> None:
        with patch(
            "custom_components.vacances_scolaires_fr.coordinator.VacancesScolairesAPI"
        ) as mock_api_cls:
            coordinator = VacancesDataUpdateCoordinator(hass, mock_entry, ZONE, ACADEMY)
        mock_api_cls.assert_called_once_with(
            ZONE,
            ACADEMY,
            hass.config.path(),
            verify_ssl=True,
            custom_timezone="Europe/Paris",
        )
        assert coordinator.zone == ZONE
        assert coordinator.academy == ACADEMY

    async def test_uses_update_interval_from_entry(
        self, hass: HomeAssistant, mock_entry: MagicMock
    ) -> None:
        mock_entry.data["update_interval"] = 3
        with patch(
            "custom_components.vacances_scolaires_fr.coordinator.VacancesScolairesAPI"
        ):
            coordinator = VacancesDataUpdateCoordinator(hass, mock_entry, ZONE, ACADEMY)
        assert coordinator.update_interval.days == 3

    async def test_options_override_data(
        self, hass: HomeAssistant, mock_entry: MagicMock
    ) -> None:
        mock_entry.options = {"update_interval": 14, "verify_ssl": False}
        with patch(
            "custom_components.vacances_scolaires_fr.coordinator.VacancesScolairesAPI"
        ) as mock_api_cls:
            VacancesDataUpdateCoordinator(hass, mock_entry, ZONE, ACADEMY)
        _, kwargs = mock_api_cls.call_args
        assert kwargs["verify_ssl"] is False


class TestCoordinatorUpdate:
    async def test_returns_dict_with_all_keys(
        self, hass: HomeAssistant, mock_entry: MagicMock
    ) -> None:
        with patch(
            "custom_components.vacances_scolaires_fr.coordinator.VacancesScolairesAPI",
            return_value=MagicMock(
                async_fetch_vacances=AsyncMock(return_value=True),
                get_vacances_en_cours=MagicMock(return_value=None),
                get_prochaines_vacances=MagicMock(return_value=None),
                get_jours_avant_vacances=MagicMock(return_value=None),
                get_jours_restants_vacances=MagicMock(return_value=None),
            ),
        ):
            coordinator = VacancesDataUpdateCoordinator(hass, mock_entry, ZONE, ACADEMY)
            data = await coordinator._async_update_data()

        assert "en_cours" in data
        assert "prochaines" in data
        assert "jours_avant" in data
        assert "jours_restants" in data

    async def test_returns_vacation_data_when_en_cours(
        self, hass: HomeAssistant, mock_entry: MagicMock
    ) -> None:
        current = MOCK_VACANCES[0]
        with patch(
            "custom_components.vacances_scolaires_fr.coordinator.VacancesScolairesAPI",
            return_value=MagicMock(
                async_fetch_vacances=AsyncMock(return_value=True),
                get_vacances_en_cours=MagicMock(return_value=current),
                get_prochaines_vacances=MagicMock(return_value=None),
                get_jours_avant_vacances=MagicMock(return_value=None),
                get_jours_restants_vacances=MagicMock(return_value=5),
            ),
        ):
            coordinator = VacancesDataUpdateCoordinator(hass, mock_entry, ZONE, ACADEMY)
            data = await coordinator._async_update_data()

        assert data["en_cours"] == current
        assert data["jours_restants"] == 5

    async def test_logs_warning_when_fetch_fails(
        self, hass: HomeAssistant, mock_entry: MagicMock
    ) -> None:
        with patch(
            "custom_components.vacances_scolaires_fr.coordinator.VacancesScolairesAPI",
            return_value=MagicMock(
                async_fetch_vacances=AsyncMock(return_value=False),
                get_vacances_en_cours=MagicMock(return_value=None),
                get_prochaines_vacances=MagicMock(return_value=None),
                get_jours_avant_vacances=MagicMock(return_value=None),
                get_jours_restants_vacances=MagicMock(return_value=None),
            ),
        ):
            coordinator = VacancesDataUpdateCoordinator(hass, mock_entry, ZONE, ACADEMY)
            data = await coordinator._async_update_data()

        assert data["en_cours"] is None
