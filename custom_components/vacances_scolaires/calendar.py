"""Calendar entity for vacances_scolaires_fr integration."""

from datetime import datetime

from homeassistant.components.calendar import CalendarEntity, CalendarEvent
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .const import CONF_ZONE, CONF_ACADEMY, DOMAIN
from .sensor import VacancesDataUpdateCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up calendar platform from a config entry."""
    zone = entry.data[CONF_ZONE]
    academy = entry.data.get(CONF_ACADEMY, "")

    # Get coordinator from hass.data (created in __init__.py)
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]

    async_add_entities([VacancesScholairesCalendar(coordinator, zone, academy)])


class VacancesScholairesCalendar(CoordinatorEntity, CalendarEntity):
    """Calendar entity for school holidays."""

    _attr_name = "Vacances scolaires"
    _attr_icon = "mdi:calendar"

    def __init__(self, coordinator: VacancesDataUpdateCoordinator, zone: str, academy: str = "") -> None:
        """Initialize calendar."""
        super().__init__(coordinator)
        self.zone = zone
        self.academy = academy
        self._attr_unique_id = f"vacances_scolaires_calendar_{zone}_{academy}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, f"vacances_scolaires_{zone}_{academy}")},
            name=f"Vacances scolaires - Zone {zone} ({academy})",
            manufacturer="Ministère de l'Éducation",
            model="Calendrier scolaire",
        )
        self.api = coordinator.api

    @property
    def device_info(self) -> DeviceInfo:
        """Return device information."""
        return self._attr_device_info

    @property
    def event(self) -> CalendarEvent | None:
        """Return the next upcoming event."""
        prochaines = self.coordinator.data.get("prochaines")
        if prochaines:
            return CalendarEvent(
                summary=prochaines["name"],
                start=prochaines["start"],
                end=prochaines["end"],
                description=f"Zone {self.zone}",
            )
        return None

    async def async_get_events(
        self, hass: HomeAssistant, start_date: datetime, end_date: datetime
    ) -> list[CalendarEvent]:
        """Return events in the given date range."""
        events = []
        all_vacances = self.api.get_all_vacances_for_calendar()

        for vacances in all_vacances:
            # Only include events that overlap with the requested date range
            if vacances["end"] >= start_date.date() and vacances["start"] <= end_date.date():
                events.append(
                    CalendarEvent(
                        summary=vacances["name"],
                        start=vacances["start"],
                        end=vacances["end"],
                        description=f"Zone {self.zone} - {self.academy}",
                    )
                )

        return events
