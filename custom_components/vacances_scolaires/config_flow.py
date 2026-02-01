"""Config flow for vacances_scolaires_fr integration."""

from typing import Any, Dict, Optional

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback

from .const import (
    CONF_ZONE,
    CONF_ACADEMY,
    CONF_UPDATE_INTERVAL,
    CONF_VERIFY_SSL,
    CONF_CREATE_CALENDAR,
    CONF_TIMEZONE,
    DEFAULT_UPDATE_INTERVAL,
    DEFAULT_VERIFY_SSL,
    DEFAULT_CREATE_CALENDAR,
    DEFAULT_TIMEZONE,
    DOMAIN,
    ZONES,
    ZONES_DOMTOM,
    ALL_ZONES,
    ZONES_ACADEMIES,
    ZONE_TIMEZONES,
)


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

        # Zones métropolitaines
        zones_info_parts.append("=== MÉTROPOLE ===")
        for zone in ZONES:
            academies = ZONES_ACADEMIES.get(zone, {})
            academy_count = len(academies)
            zone_choices[zone] = f"Zone {zone} - Métropole ({academy_count} académies)"

            academy_names = ", ".join(list(academies.keys())[:3])
            if academy_count > 3:
                academy_names += f"... (+{academy_count - 3})"
            zones_info_parts.append(f"Zone {zone}: {academy_names}")

        # Zones DOM-TOM
        zones_info_parts.append("\n=== DOM-TOM ===")
        for zone in ZONES_DOMTOM:
            timezone_info = ZONE_TIMEZONES.get(zone, "Europe/Paris")
            # Extraire le décalage UTC du timezone (simplifié)
            utc_offset = timezone_info.split("/")[-1]
            zone_choices[zone] = f"{zone} ({timezone_info})"
            zones_info_parts.append(f"{zone}: {timezone_info}")

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
            # Create the config entry with selected zone, academy, and default options
            academy = user_input[CONF_ACADEMY]
            update_interval = user_input.get(CONF_UPDATE_INTERVAL, DEFAULT_UPDATE_INTERVAL)
            verify_ssl = user_input.get(CONF_VERIFY_SSL, DEFAULT_VERIFY_SSL)
            create_calendar = user_input.get(CONF_CREATE_CALENDAR, DEFAULT_CREATE_CALENDAR)

            # Déterminer le timezone par défaut pour la zone
            default_timezone = ZONE_TIMEZONES.get(self._selected_zone, DEFAULT_TIMEZONE)
            timezone = user_input.get(CONF_TIMEZONE, default_timezone)

            # Titre différent pour DOM-TOM (pas de "Zone")
            if self._selected_zone in ZONES:
                title = f"Vacances scolaires - Zone {self._selected_zone} ({academy})"
            else:
                title = f"Vacances scolaires - {self._selected_zone}"

            return self.async_create_entry(
                title=title,
                data={
                    CONF_ZONE: self._selected_zone,
                    CONF_ACADEMY: academy,
                    CONF_TIMEZONE: timezone,
                    CONF_UPDATE_INTERVAL: update_interval,
                    CONF_VERIFY_SSL: verify_ssl,
                    CONF_CREATE_CALENDAR: create_calendar,
                },
            )

        # Get academies and timezone for the selected zone
        academies = ZONES_ACADEMIES.get(self._selected_zone, {})
        default_timezone = ZONE_TIMEZONES.get(self._selected_zone, DEFAULT_TIMEZONE)

        # Create academy choices with full descriptions
        academy_choices = {}
        for academy_key, academy_desc in academies.items():
            academy_choices[academy_key] = academy_desc

        schema = vol.Schema(
            {
                vol.Required(CONF_ACADEMY): vol.In(academy_choices),
                vol.Optional(CONF_TIMEZONE, default=default_timezone): str,
                vol.Optional(
                    CONF_UPDATE_INTERVAL,
                    default=DEFAULT_UPDATE_INTERVAL
                ): vol.All(vol.Coerce(int), vol.Range(min=1, max=30)),
                vol.Optional(
                    CONF_VERIFY_SSL,
                    default=DEFAULT_VERIFY_SSL
                ): bool,
                vol.Optional(
                    CONF_CREATE_CALENDAR,
                    default=DEFAULT_CREATE_CALENDAR
                ): bool,
            }
        )

        return self.async_show_form(
            step_id="academy",
            data_schema=schema,
            description_placeholders={
                "zone": self._selected_zone,
                "timezone": default_timezone,
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
        """Manage the options - main menu."""
        if user_input is not None:
            choice = user_input.get("option_type")
            if choice == "zone_academy":
                return await self.async_step_zone()
            elif choice == "advanced":
                return await self.async_step_advanced()

        # Get current configuration
        current_zone = self.config_entry.data.get(CONF_ZONE)
        current_academy = self.config_entry.data.get(CONF_ACADEMY)

        schema = vol.Schema(
            {
                vol.Required("option_type"): vol.In({
                    "zone_academy": f"Zone et Académie (actuellement: Zone {current_zone}, {current_academy})",
                    "advanced": "Options avancées (intervalle, SSL, calendrier)",
                }),
            }
        )

        return self.async_show_form(
            step_id="init",
            data_schema=schema,
        )

    async def async_step_zone(
        self, user_input: Optional[Dict[str, Any]] = None
    ) -> config_entries.FlowResult:
        """Manage zone selection."""
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

        # Zones métropolitaines
        zones_info_parts.append("=== MÉTROPOLE ===")
        for zone in ZONES:
            academies = ZONES_ACADEMIES.get(zone, {})
            academy_count = len(academies)
            zone_choices[zone] = f"Zone {zone} - Métropole ({academy_count} académies)"

            academy_names = ", ".join(list(academies.keys())[:3])
            if academy_count > 3:
                academy_names += f"... (+{academy_count - 3})"
            zones_info_parts.append(f"Zone {zone}: {academy_names}")

        # Zones DOM-TOM
        zones_info_parts.append("\n=== DOM-TOM ===")
        for zone in ZONES_DOMTOM:
            timezone_info = ZONE_TIMEZONES.get(zone, "Europe/Paris")
            zone_choices[zone] = f"{zone} ({timezone_info})"
            zones_info_parts.append(f"{zone}: {timezone_info}")

        schema = vol.Schema(
            {
                vol.Required(CONF_ZONE, default=current_zone): vol.In(zone_choices),
            }
        )

        return self.async_show_form(
            step_id="zone",
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

            # Preserve existing options
            new_data = {
                CONF_ZONE: self._selected_zone,
                CONF_ACADEMY: academy,
            }

            # Update timezone based on new zone
            new_timezone = ZONE_TIMEZONES.get(self._selected_zone, DEFAULT_TIMEZONE)
            new_data[CONF_TIMEZONE] = new_timezone

            # Preserve advanced options from current data or use defaults
            new_data[CONF_UPDATE_INTERVAL] = self.config_entry.data.get(
                CONF_UPDATE_INTERVAL, DEFAULT_UPDATE_INTERVAL
            )
            new_data[CONF_VERIFY_SSL] = self.config_entry.data.get(
                CONF_VERIFY_SSL, DEFAULT_VERIFY_SSL
            )
            new_data[CONF_CREATE_CALENDAR] = self.config_entry.data.get(
                CONF_CREATE_CALENDAR, DEFAULT_CREATE_CALENDAR
            )

            # Titre différent pour DOM-TOM (pas de "Zone")
            if self._selected_zone in ZONES:
                title = f"Vacances scolaires - Zone {self._selected_zone} ({academy})"
            else:
                title = f"Vacances scolaires - {self._selected_zone}"

            # Update the config entry data
            self.hass.config_entries.async_update_entry(
                self.config_entry,
                data=new_data,
                title=title,
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

    async def async_step_advanced(
        self, user_input: Optional[Dict[str, Any]] = None
    ) -> config_entries.FlowResult:
        """Handle advanced options."""
        if user_input is not None:
            # Update options with new values while preserving zone/academy
            new_data = {
                CONF_ZONE: self.config_entry.data.get(CONF_ZONE),
                CONF_ACADEMY: self.config_entry.data.get(CONF_ACADEMY),
                CONF_UPDATE_INTERVAL: user_input.get(CONF_UPDATE_INTERVAL, DEFAULT_UPDATE_INTERVAL),
                CONF_VERIFY_SSL: user_input.get(CONF_VERIFY_SSL, DEFAULT_VERIFY_SSL),
                CONF_CREATE_CALENDAR: user_input.get(CONF_CREATE_CALENDAR, DEFAULT_CREATE_CALENDAR),
            }

            # Store in options for dynamic updates
            self.hass.config_entries.async_update_entry(
                self.config_entry,
                data=new_data,
                options={
                    CONF_UPDATE_INTERVAL: new_data[CONF_UPDATE_INTERVAL],
                    CONF_VERIFY_SSL: new_data[CONF_VERIFY_SSL],
                    CONF_CREATE_CALENDAR: new_data[CONF_CREATE_CALENDAR],
                },
            )

            # Reload the integration to apply changes
            await self.hass.config_entries.async_reload(self.config_entry.entry_id)

            return self.async_create_entry(title="", data={})

        # Get current values
        current_update_interval = self.config_entry.options.get(
            CONF_UPDATE_INTERVAL,
            self.config_entry.data.get(CONF_UPDATE_INTERVAL, DEFAULT_UPDATE_INTERVAL)
        )
        current_verify_ssl = self.config_entry.options.get(
            CONF_VERIFY_SSL,
            self.config_entry.data.get(CONF_VERIFY_SSL, DEFAULT_VERIFY_SSL)
        )
        current_create_calendar = self.config_entry.options.get(
            CONF_CREATE_CALENDAR,
            self.config_entry.data.get(CONF_CREATE_CALENDAR, DEFAULT_CREATE_CALENDAR)
        )

        schema = vol.Schema(
            {
                vol.Optional(
                    CONF_UPDATE_INTERVAL,
                    default=current_update_interval
                ): vol.All(vol.Coerce(int), vol.Range(min=1, max=30)),
                vol.Optional(
                    CONF_VERIFY_SSL,
                    default=current_verify_ssl
                ): bool,
                vol.Optional(
                    CONF_CREATE_CALENDAR,
                    default=current_create_calendar
                ): bool,
            }
        )

        return self.async_show_form(
            step_id="advanced",
            data_schema=schema,
            description_placeholders={
                "current_interval": str(current_update_interval),
                "current_ssl": "Oui" if current_verify_ssl else "Non",
                "current_calendar": "Oui" if current_create_calendar else "Non",
            },
        )
