"""Sensors for vacances_scolaires_fr integration."""

import logging
from datetime import timedelta
from typing import Any

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
    UpdateFailed,
)

from .api import VacancesScolairesAPI
from .const import (
    ATTR_DAYS_UNTIL,
    ATTR_VACANCES_END,
    ATTR_VACANCES_NAME,
    ATTR_VACANCES_START,
    ATTR_VACANCES_ZONE,
    ATTR_ACADEMY,
    CONF_ZONE,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up sensor platform from a config entry."""
    zone = entry.data[CONF_ZONE]
    academy = entry.data.get("academy", "")

    # Get coordinator from hass.data (created in __init__.py)
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]

    entities = [
        ProchainevacancesSensor(coordinator, zone, academy),
        JoursAvantVacancesSensor(coordinator, zone, academy),
        ZoneScholaireSensor(coordinator, zone, academy),
    ]

    async_add_entities(entities)


class VacancesDataUpdateCoordinator(DataUpdateCoordinator):
    """Coordinator to manage vacances scolaires data."""

    def __init__(self, hass: HomeAssistant, zone: str, academy: str = "") -> None:
        """Initialize coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=f"Vacances scolaires Zone {zone}",
            update_interval=timedelta(days=7),  # Update weekly to check for API changes
        )
        self.api = VacancesScolairesAPI(zone, academy, hass.config.path())
        self.zone = zone
        self.academy = academy

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


class ProchainevacancesSensor(CoordinatorEntity, SensorEntity):
    """Sensor for next school holidays."""

    _attr_name = "Prochaines vacances"
    _attr_unique_id = "prochaines_vacances"
    _attr_icon = "mdi:calendar-clock"

    def __init__(self, coordinator: VacancesDataUpdateCoordinator, zone: str, academy: str = "") -> None:
        """Initialize sensor."""
        super().__init__(coordinator)
        self.zone = zone
        self.academy = academy
        self._attr_unique_id = f"prochaines_vacances_{zone}_{academy}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, f"vacances_scolaires_{zone}_{academy}")},
            name=f"Vacances scolaires - Zone {zone} ({academy})",
            manufacturer="Ministère de l'Éducation",
            model="Calendrier scolaire",
        )

    @property
    def device_info(self) -> DeviceInfo:
        """Return device information."""
        return self._attr_device_info

    @property
    def state(self) -> str | None:
        """Return sensor state (date of next vacances start)."""
        vacances = self.coordinator.data.get("prochaines")
        return vacances["start"].isoformat() if vacances else None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return entity specific state attributes."""
        vacances = self.coordinator.data.get("prochaines")
        attrs = {}

        if vacances:
            attrs[ATTR_VACANCES_NAME] = vacances["name"]
            attrs[ATTR_VACANCES_START] = vacances["start"].isoformat()
            attrs[ATTR_VACANCES_END] = vacances["end"].isoformat()
            attrs[ATTR_VACANCES_ZONE] = self.zone
            attrs[ATTR_ACADEMY] = self.academy
            attrs[ATTR_DAYS_UNTIL] = self.coordinator.data.get("jours_avant", 0)

        return attrs


class JoursAvantVacancesSensor(CoordinatorEntity, SensorEntity):
    """Sensor for days until next school holidays."""

    _attr_name = "Jours avant vacances"
    _attr_unique_id = "jours_avant_vacances"
    _attr_icon = "mdi:calendar-range"
    _attr_unit_of_measurement = "jours"

    def __init__(self, coordinator: VacancesDataUpdateCoordinator, zone: str, academy: str = "") -> None:
        """Initialize sensor."""
        super().__init__(coordinator)
        self.zone = zone
        self.academy = academy
        self._attr_unique_id = f"jours_avant_vacances_{zone}_{academy}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, f"vacances_scolaires_{zone}_{academy}")},
            name=f"Vacances scolaires - Zone {zone} ({academy})",
            manufacturer="Ministère de l'Éducation",
            model="Calendrier scolaire",
        )

    @property
    def device_info(self) -> DeviceInfo:
        """Return device information."""
        return self._attr_device_info

    @property
    def state(self) -> int | None:
        """Return sensor state."""
        return self.coordinator.data.get("jours_avant")


class ZoneScholaireSensor(CoordinatorEntity, SensorEntity):
    """Sensor for the school zone."""

    _attr_name = "Zone scolaire"
    _attr_unique_id = "zone_scolaire"
    _attr_icon = "mdi:map-marker"

    def __init__(self, coordinator: VacancesDataUpdateCoordinator, zone: str, academy: str = "") -> None:
        """Initialize sensor."""
        super().__init__(coordinator)
        self.zone = zone
        self.academy = academy
        self._attr_unique_id = f"zone_scolaire_{zone}_{academy}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, f"vacances_scolaires_{zone}_{academy}")},
            name=f"Vacances scolaires - Zone {zone} ({academy})",
            manufacturer="Ministère de l'Éducation",
            model="Calendrier scolaire",
        )

    @property
    def device_info(self) -> DeviceInfo:
        """Return device information."""
        return self._attr_device_info

    @property
    def state(self) -> str:
        """Return sensor state."""
        return self.zone

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return entity specific state attributes."""
        return {
            ATTR_VACANCES_ZONE: self.zone,
            ATTR_ACADEMY: self.academy,
        }
