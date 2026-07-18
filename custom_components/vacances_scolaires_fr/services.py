"""Services for vacances_scolaires_fr integration."""

import logging

import voluptuous as vol
from homeassistant.core import HomeAssistant, ServiceCall, callback
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import selector, service

from .const import CONF_CONFIG_ENTRY, DOMAIN, SERVICE_CLEAR_CACHE
from .coordinator import VacancesDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)


@callback
def async_setup_services(hass: HomeAssistant) -> None:
    """Register the vacances_scolaires_fr services."""

    async def clear_cache(call: ServiceCall) -> None:
        """Handle a clear cache service call and trigger a refresh."""
        entry = service.async_get_config_entry(
            call.hass, DOMAIN, call.data[CONF_CONFIG_ENTRY]
        )
        coordinator: VacancesDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id][
            "coordinator"
        ]

        try:
            await coordinator.api.async_clear_cache()
        except OSError as exc:
            raise HomeAssistantError(
                translation_domain=DOMAIN,
                translation_key="clear_cache_failed",
                translation_placeholders={"error": str(exc)},
            ) from exc

        await coordinator.async_request_refresh()

    hass.services.async_register(
        DOMAIN,
        SERVICE_CLEAR_CACHE,
        clear_cache,
        vol.Schema(
            {
                vol.Required(CONF_CONFIG_ENTRY): selector.ConfigEntrySelector(
                    {
                        "integration": DOMAIN,
                    }
                ),
            }
        ),
    )
