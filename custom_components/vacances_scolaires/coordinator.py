"""Data update coordinator for vacances_scolaires_fr integration."""

import logging
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import VacancesScolairesAPI
from .const import CONF_UPDATE_INTERVAL, CONF_VERIFY_SSL, CONF_TIMEZONE, DEFAULT_UPDATE_INTERVAL, DEFAULT_VERIFY_SSL, DEFAULT_TIMEZONE

_LOGGER = logging.getLogger(__name__)


class VacancesDataUpdateCoordinator(DataUpdateCoordinator):
    """Coordinator to manage vacances scolaires data."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry, zone: str, academy: str = "") -> None:
        """Initialize coordinator."""
        self.entry = entry

        # Get update interval from options or config
        update_interval_days = entry.options.get(
            CONF_UPDATE_INTERVAL,
            entry.data.get(CONF_UPDATE_INTERVAL, DEFAULT_UPDATE_INTERVAL)
        )

        # Get verify_ssl from options or config
        verify_ssl = entry.options.get(
            CONF_VERIFY_SSL,
            entry.data.get(CONF_VERIFY_SSL, DEFAULT_VERIFY_SSL)
        )

        # Get custom timezone from config
        custom_timezone = entry.data.get(CONF_TIMEZONE, DEFAULT_TIMEZONE)

        super().__init__(
            hass,
            _LOGGER,
            name=f"Vacances scolaires Zone {zone}",
            update_interval=timedelta(days=update_interval_days),
        )
        self.api = VacancesScolairesAPI(
            zone,
            academy,
            hass.config.path(),
            verify_ssl=verify_ssl,
            custom_timezone=custom_timezone
        )
        self.zone = zone
        self.academy = academy
        self.verify_ssl = verify_ssl
        self.timezone = custom_timezone

    async def _async_update_data(self) -> dict:
        """Fetch data from the API."""
        try:
            # Try to fetch fresh data from API
            success = await self.api.async_fetch_vacances()
            if not success:
                raise UpdateFailed("Failed to fetch vacances data from API")
            return self._get_data()
        except Exception as err:
            _LOGGER.error(f"Error fetching vacances: {err}", exc_info=True)
            raise UpdateFailed(f"Error fetching vacances: {err}") from err

    def _get_data(self) -> dict:
        """Get fresh data from API."""
        return {
            "en_cours": self.api.get_vacances_en_cours(),
            "prochaines": self.api.get_prochaines_vacances(),
            "jours_avant": self.api.get_jours_avant_vacances(),
            "jours_restants": self.api.get_jours_restants_vacances(),
        }
