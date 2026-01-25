"""Config flow for vacances_scolaires_fr integration."""

from typing import Any, Dict, Optional

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback

from .const import CONF_ZONE, CONF_ACADEMY, DOMAIN, ZONES, ZONES_ACADEMIES


class VacancesScolairesConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for vacances_scolaires_fr."""

    VERSION = 1

    def __init__(self):
        """Initialize the config flow."""
        self._selected_zone: Optional[str] = None

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Get the options flow for this handler."""
        return VacancesScolairesOptionsFlow(config_entry)

    async def async_step_user(
        self, user_input: Optional[Dict[str, Any]] = None
    ) -> config_entries.FlowResult:
        """Handle the initial step (zone selection)."""
        # Check if there's already a config entry
        await self.async_set_unique_id("vacances_scolaires_fr")
        self._abort_if_unique_id_configured()

        if user_input is not None:
            # Store the selected zone and move to academy selection
            self._selected_zone = user_input[CONF_ZONE]
            return await self.async_step_academy()

        # Create zone choices with description and academies list
        zone_choices = {}
        zones_info_parts = []

        for zone in ZONES:
            academies = ZONES_ACADEMIES.get(zone, {})
            academy_count = len(academies)
            zone_choices[zone] = f"Zone {zone} ({academy_count} académies)"

            academy_names = ", ".join(academies.keys())
            zones_info_parts.append(f"Zone {zone}: {academy_names}")

        schema = vol.Schema(
            {
                vol.Required(CONF_ZONE): vol.In(zone_choices),
            }
        )

        return self.async_show_form(
            step_id="user",
            data_schema=schema,
            description_placeholders={
                "zones_info": "\n".join(zones_info_parts)
            },
        )

    async def async_step_academy(
        self, user_input: Optional[Dict[str, Any]] = None
    ) -> config_entries.FlowResult:
        """Handle the academy selection step."""
        if user_input is not None:
            # Create the config entry with selected zone and academy
            academy = user_input[CONF_ACADEMY]
            return self.async_create_entry(
                title=f"Vacances scolaires - Zone {self._selected_zone} ({academy})",
                data={
                    CONF_ZONE: self._selected_zone,
                    CONF_ACADEMY: academy,
                },
            )

        # Get academies for the selected zone
        academies = ZONES_ACADEMIES.get(self._selected_zone, {})

        # Create academy choices with full descriptions
        academy_choices = {}
        for academy_key, academy_desc in academies.items():
            academy_choices[academy_key] = academy_desc

        schema = vol.Schema(
            {
                vol.Required(CONF_ACADEMY): vol.In(academy_choices),
            }
        )

        return self.async_show_form(
            step_id="academy",
            data_schema=schema,
            description_placeholders={
                "zone": self._selected_zone,
            },
        )


class VacancesScolairesOptionsFlow(config_entries.OptionsFlow):
    """Handle options flow for vacances_scolaires_fr."""

    def __init__(self, config_entry: config_entries.ConfigEntry):
        """Initialize options flow."""
        self.config_entry = config_entry
        self._selected_zone: Optional[str] = None

    async def async_step_init(
        self, user_input: Optional[Dict[str, Any]] = None
    ) -> config_entries.FlowResult:
        """Manage the options - zone selection."""
        if user_input is not None:
            # Store the selected zone and move to academy selection
            self._selected_zone = user_input[CONF_ZONE]
            return await self.async_step_academy()

        # Get current configuration
        current_zone = self.config_entry.data.get(CONF_ZONE)
        current_academy = self.config_entry.data.get(CONF_ACADEMY)

        # Create zone choices with description and academies list
        zone_choices = {}
        zones_info_parts = []

        for zone in ZONES:
            academies = ZONES_ACADEMIES.get(zone, {})
            academy_count = len(academies)
            zone_choices[zone] = f"Zone {zone} ({academy_count} académies)"

            academy_names = ", ".join(academies.keys())
            zones_info_parts.append(f"Zone {zone}: {academy_names}")

        schema = vol.Schema(
            {
                vol.Required(CONF_ZONE, default=current_zone): vol.In(zone_choices),
            }
        )

        return self.async_show_form(
            step_id="init",
            data_schema=schema,
            description_placeholders={
                "zones_info": "\n".join(zones_info_parts),
                "current_zone": current_zone,
                "current_academy": current_academy,
            },
        )

    async def async_step_academy(
        self, user_input: Optional[Dict[str, Any]] = None
    ) -> config_entries.FlowResult:
        """Handle the academy selection step in options."""
        if user_input is not None:
            # Update the config entry with new zone and academy
            academy = user_input[CONF_ACADEMY]

            # Update the config entry data
            self.hass.config_entries.async_update_entry(
                self.config_entry,
                data={
                    CONF_ZONE: self._selected_zone,
                    CONF_ACADEMY: academy,
                },
                title=f"Vacances scolaires - Zone {self._selected_zone} ({academy})",
            )

            # Reload the integration to apply changes
            await self.hass.config_entries.async_reload(self.config_entry.entry_id)

            return self.async_create_entry(title="", data={})

        # Get current academy for default value
        current_academy = self.config_entry.data.get(CONF_ACADEMY)

        # Get academies for the selected zone
        academies = ZONES_ACADEMIES.get(self._selected_zone, {})

        # Create academy choices with full descriptions
        academy_choices = {}
        for academy_key, academy_desc in academies.items():
            academy_choices[academy_key] = academy_desc

        # Set default to current academy if it's in the new zone, otherwise first academy
        default_academy = current_academy if current_academy in academies else list(academies.keys())[0]

        schema = vol.Schema(
            {
                vol.Required(CONF_ACADEMY, default=default_academy): vol.In(academy_choices),
            }
        )

        return self.async_show_form(
            step_id="academy",
            data_schema=schema,
            description_placeholders={
                "zone": self._selected_zone,
            },
        )
