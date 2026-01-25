"""Binary sensors for vacances_scolaires_fr integration."""

from typing import Any

from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .const import (
    ATTR_DAYS_REMAINING,
    ATTR_VACANCES_END,
    ATTR_VACANCES_NAME,
    ATTR_VACANCES_START,
    ATTR_VACANCES_ZONE,
    ATTR_ACADEMY,
    CONF_ZONE,
    DOMAIN,
)
from .sensor import VacancesDataUpdateCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up binary sensor platform from a config entry."""
    zone = entry.data[CONF_ZONE]
    academy = entry.data.get("academy", "")

    # Get coordinator from hass.data (created in __init__.py)
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]

    async_add_entities([VacancesEnCoursBinarySensor(coordinator, zone, academy)])


class VacancesEnCoursBinarySensor(CoordinatorEntity, BinarySensorEntity):
    """Binary sensor for current school holidays."""

    _attr_name = "Vacances en cours"
    _attr_unique_id = "vacances_en_cours"
    _attr_icon = "mdi:calendar-check"
    _attr_device_class = "occupancy"

    def __init__(
        self, coordinator: VacancesDataUpdateCoordinator, zone: str, academy: str = ""
    ) -> None:
        """Initialize binary sensor."""
        super().__init__(coordinator)
        self.zone = zone
        self.academy = academy
        self._attr_unique_id = f"vacances_en_cours_{zone}_{academy}"
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
    def is_on(self) -> bool:
        """Return True if currently on vacation."""
        vacances = self.coordinator.data.get("en_cours")
        return vacances is not None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return entity specific state attributes."""
        vacances = self.coordinator.data.get("en_cours")
        attrs = {}

        if vacances:
            attrs[ATTR_VACANCES_NAME] = vacances["name"]
            attrs[ATTR_VACANCES_START] = vacances["start"].isoformat()
            attrs[ATTR_VACANCES_END] = vacances["end"].isoformat()
            attrs[ATTR_VACANCES_ZONE] = self.zone
            attrs[ATTR_ACADEMY] = self.academy
            attrs[ATTR_DAYS_REMAINING] = self.coordinator.data.get("jours_restants", 0)

        return attrs
