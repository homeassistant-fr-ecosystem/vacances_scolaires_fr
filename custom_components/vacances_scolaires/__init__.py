"""The vacances_scolaires_fr integration."""

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN, CONF_ZONE, CONF_CREATE_CALENDAR, DEFAULT_CREATE_CALENDAR
from .coordinator import VacancesDataUpdateCoordinator


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up vacances_scolaires_fr from a config entry."""
    hass.data.setdefault(DOMAIN, {})

    # Create coordinator once and store it
    zone = entry.data[CONF_ZONE]
    academy = entry.data.get("academy", "")
    coordinator = VacancesDataUpdateCoordinator(hass, entry, zone, academy)
    await coordinator.async_config_entry_first_refresh()

    hass.data[DOMAIN][entry.entry_id] = {
        "coordinator": coordinator,
        "entry_data": entry.data,
    }

    # Setup basic platforms (sensor and binary_sensor always loaded)
    platforms = ["sensor", "binary_sensor"]

    # Add calendar platform if requested
    create_calendar = entry.options.get(
        CONF_CREATE_CALENDAR,
        entry.data.get(CONF_CREATE_CALENDAR, DEFAULT_CREATE_CALENDAR)
    )

    if create_calendar:
        platforms.append("calendar")

    await hass.config_entries.async_forward_entry_setups(entry, platforms)

    # Register update listener for options changes
    entry.async_on_unload(entry.add_update_listener(async_reload_entry))

    return True


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload config entry when options change."""
    await hass.config_entries.async_reload(entry.entry_id)


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    # Determine which platforms were loaded
    platforms = ["sensor", "binary_sensor"]

    create_calendar = entry.options.get(
        CONF_CREATE_CALENDAR,
        entry.data.get(CONF_CREATE_CALENDAR, DEFAULT_CREATE_CALENDAR)
    )

    if create_calendar:
        platforms.append("calendar")

    unload_ok = await hass.config_entries.async_unload_platforms(entry, platforms)

    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
