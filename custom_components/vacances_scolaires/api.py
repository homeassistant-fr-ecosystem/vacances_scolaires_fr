"""API logic for vacances_scolaires_fr integration."""

from datetime import date, datetime
from typing import Optional
from zoneinfo import ZoneInfo
import aiohttp
import asyncio
import bisect
import logging
import json
import os
import re

from .const import ZONES_ACADEMIES, ZONES, ZONES_DOMTOM, ZONE_TIMEZONES

_LOGGER = logging.getLogger(__name__)

API_URL = "https://catalogue.data.gouv.fr/api/1/datasets/calendrier-scolaire-en-france"
VACANCES_API_URL = "https://data.education.gouv.fr/api/explore/v2.1/catalog/datasets/fr-en-calendrier-scolaire/records"
CACHE_VALIDITY_DAYS = 7  # Cache valid for 7 days
API_TIMEOUT = 10  # Timeout in seconds for API requests
API_LIMIT = 100  # Maximum number of records to fetch


class VacancesScolairesAPI:
    """Handle vacances scolaires data and logic."""

    def __init__(self, zone: str, academy: Optional[str] = None, hass_config_path: Optional[str] = None, verify_ssl: bool = True, custom_timezone: Optional[str] = None):
        """Initialize API with selected zone and optional academy."""
        # Validate zone (métropole ou DOM-TOM)
        all_zones = ZONES + ZONES_DOMTOM
        if zone not in all_zones:
            raise ValueError(f"Invalid zone '{zone}'. Must be one of: {', '.join(all_zones)}")

        self.zone = zone
        self.verify_ssl = verify_ssl

        # If no academy provided, use the first one from the zone's academy list
        if academy:
            # Validate academy belongs to the zone
            zone_academies = ZONES_ACADEMIES.get(zone, {})
            if academy not in zone_academies:
                raise ValueError(f"Invalid academy '{academy}' for zone {zone}. Must be one of: {', '.join(zone_academies.keys())}")
            self.academy = academy
        else:
            zone_academies = ZONES_ACADEMIES.get(zone, {})
            self.academy = list(zone_academies.keys())[0] if zone_academies else zone

        # Déterminer le fuseau horaire
        self.timezone_str = custom_timezone or ZONE_TIMEZONES.get(zone, "Europe/Paris")
        try:
            self.timezone = ZoneInfo(self.timezone_str)
        except Exception as e:
            _LOGGER.warning("Invalid timezone %s, falling back to Europe/Paris: %s",
                          self.timezone_str, e)
            self.timezone = ZoneInfo("Europe/Paris")
            self.timezone_str = "Europe/Paris"

        # Set cache directory (instance variable instead of global)
        if hass_config_path:
            self._cache_dir = os.path.join(hass_config_path, ".storage", "vacances_scolaires")
        else:
            self._cache_dir = None

        self._vacances = []
        self._use_static_data = True
        _LOGGER.info("Initialized API for Zone %s, Academy: %s, Timezone: %s, verify_ssl: %s",
                    zone, self.academy, self.timezone_str, verify_ssl)

    async def _ensure_cache_dir(self) -> None:
        """Ensure the cache directory exists."""
        if self._cache_dir:
            await asyncio.to_thread(os.makedirs, self._cache_dir, mode=0o700, exist_ok=True)

    def _get_cache_path(self) -> Optional[str]:
        """Get the cache file path for this zone and academy."""
        if not self._cache_dir:
            return None
        # Sanitize academy name to prevent path injection
        # Only allow alphanumeric, underscore, and hyphen characters
        safe_academy = re.sub(r'[^\w\-]', '_', self.academy)
        safe_zone = re.sub(r'[^\w\-]', '_', self.zone)
        return os.path.join(self._cache_dir, f"vacances_{safe_zone}_{safe_academy}.json")

    async def _is_cache_valid(self) -> bool:
        """Check if cache file exists and is still valid."""
        return await asyncio.to_thread(self._is_cache_valid_sync)

    def _is_cache_valid_sync(self) -> bool:
        """Check if cache file exists and is still valid (sync)."""
        cache_path = self._get_cache_path()
        if not cache_path or not os.path.exists(cache_path):
            return False

        try:
            file_age = datetime.now() - datetime.fromtimestamp(os.path.getmtime(cache_path))
            return file_age.days < CACHE_VALIDITY_DAYS
        except Exception as e:
            _LOGGER.debug("Error checking cache validity: %s", e)
            return False

    def _load_from_cache_sync(self) -> bool:
        """Load vacances data from cache file (sync operation)."""
        cache_path = self._get_cache_path()
        if not cache_path or not os.path.exists(cache_path):
            return False

        try:
            with open(cache_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            self._parse_api_data(data)
            _LOGGER.info("Loaded %d vacation periods from cache for Zone %s, Academy %s", len(self._vacances), self.zone, self.academy)
            return True
        except Exception as e:
            _LOGGER.warning("Failed to load cache for Zone %s, Academy %s: %s", self.zone, self.academy, e)
            return False

    async def _load_from_cache(self) -> bool:
        """Load vacances data from cache file."""
        return await asyncio.to_thread(self._load_from_cache_sync)

    def _save_to_cache_sync(self, data: dict) -> None:
        """Save API response to cache file (sync operation)."""
        cache_path = self._get_cache_path()
        if not cache_path:
            return

        try:
            with open(cache_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            _LOGGER.debug("Cached vacances data for Zone %s, Academy %s", self.zone, self.academy)
        except Exception as e:
            _LOGGER.warning("Failed to save cache for Zone %s, Academy %s: %s", self.zone, self.academy, e)

    async def _save_to_cache(self, data: dict) -> None:
        """Save API response to cache file."""
        await asyncio.to_thread(self._save_to_cache_sync, data)

    async def async_fetch_vacances(self) -> bool:
        """Fetch vacances from data.gouv.fr API with caching."""
        # Ensure cache directory exists
        await self._ensure_cache_dir()

        # Try to load from cache first
        if await self._is_cache_valid():
            return await self._load_from_cache()

        # If cache is invalid or doesn't exist, fetch from API
        try:
            # Create SSL context based on verify_ssl setting
            ssl_context = None if self.verify_ssl else False

            async with aiohttp.ClientSession() as session:
                # Fetch vacances data with zone and academy filters
                # Différencier métropole et DOM-TOM
                if self.zone in ZONES:
                    # Métropole : utiliser le format "Zone X"
                    zone_letter = self.zone.upper() if len(self.zone) == 1 else self.zone
                    expected_zone_format = f"Zone {zone_letter}"
                else:
                    # DOM-TOM : utiliser directement le nom de l'académie
                    expected_zone_format = None

                # Calculate current year and next year for filtering
                current_year = datetime.now().year
                next_year = current_year + 1
                start_date = f"{current_year}-01-01"
                end_date = f"{next_year}-12-31"

                # Build where clause with zone, academy, date, and population filters
                # OpenDatasoft API syntax: combine conditions with AND
                where_clauses = []

                # Pour la métropole, filtrer par zone
                if expected_zone_format:
                    where_clauses.append(f'zones="{expected_zone_format}"')

                # Add academy filter (pour métropole si spécifié, pour DOM-TOM toujours)
                if self.academy:
                    # The API uses 'location' field for academy names
                    where_clauses.append(f'location="{self.academy}"')

                # Add date range filter for current year and next year
                # Use overlap detection: vacation overlaps if it starts before range ends AND ends after range starts
                where_clauses.append(f'start_date <= "{end_date}" AND end_date >= "{start_date}"')

                # Add population filter to only get student vacations (exclude teachers)
                # population can be "-" (all) or "Élèves" (students), but not "Enseignants" (teachers)
                where_clauses.append('(population="-" OR population="Élèves")')

                where_condition = " AND ".join(where_clauses)

                params = {
                    "limit": API_LIMIT,
                    "where": where_condition,
                }
                _LOGGER.debug("Fetching from API for years %s-%s: %s with params: %s (verify_ssl=%s)", current_year, next_year, VACANCES_API_URL, params, self.verify_ssl)
                async with session.get(VACANCES_API_URL, params=params, timeout=aiohttp.ClientTimeout(total=API_TIMEOUT), ssl=ssl_context) as resp:
                    _LOGGER.debug("API response status: %d", resp.status)
                    if resp.status == 200:
                        data = await resp.json()
                        _LOGGER.debug("API response records count: %d", len(data.get('results', [])))
                        # Save to cache before parsing
                        await self._save_to_cache(data)
                        self._parse_api_data(data)
                        self._use_static_data = False
                        _LOGGER.info("Fetched %d vacation periods from API for Zone %s, Academy %s", len(self._vacances), self.zone, self.academy)
                        return True
                    else:
                        response_text = await resp.text()
                        _LOGGER.error("API returned status %d: %s", resp.status, response_text)
        except (aiohttp.ClientError, asyncio.TimeoutError) as err:
            _LOGGER.error("Failed to fetch from data.gouv.fr API: %s", err, exc_info=True)
            # Try to load from cache even if it's old
            if await self._load_from_cache():
                _LOGGER.warning("Using old cached data due to API failure")
                return True
        except json.JSONDecodeError as err:
            _LOGGER.error("Failed to parse API response as JSON: %s", err, exc_info=True)
            if await self._load_from_cache():
                _LOGGER.warning("Using old cached data due to JSON parsing failure")
                return True

        # Fallback to static data
        _LOGGER.error("No API data and no valid cache, using static data")
        self._load_static_data()
        return False

    def _parse_api_data(self, data: dict) -> None:
        """Parse API response and extract vacation periods."""
        self._vacances = []

        # Validate data structure
        if not isinstance(data, dict):
            _LOGGER.warning("API response is not a dictionary, type: %s", type(data).__name__)
            self._load_static_data()
            return

        if "results" not in data:
            _LOGGER.warning("No 'results' key in API response: %s", list(data.keys()) if hasattr(data, 'keys') else 'N/A')
            self._load_static_data()
            return

        results = data.get("results", [])
        _LOGGER.debug("Processing %d records from API for zone %s", len(results), self.zone)

        zone_letter = self.zone.upper() if len(self.zone) == 1 else self.zone
        _LOGGER.debug("Normalized zone: %s -> %s", self.zone, zone_letter)
        
        for record in results:
            try:
                # API fields: description, start_date, end_date, zones, location (academy), population
                zones_str = record.get("zones", "").strip()
                location_str = record.get("location", "").strip()
                population_str = record.get("population", "").strip()

                # Filter by population: only keep "-" (all) or "Élèves" (students)
                # Exclude "Enseignants" (teachers) vacation periods
                if population_str and population_str not in ["-", "Élèves"]:
                    _LOGGER.debug("Skipping vacation '%s' with population '%s' (only keeping '-' or 'Élèves')", record.get('description', 'N/A'), population_str)
                    continue

                # Only add if this vacation applies to our zone
                # The API returns values like "Zone A", "Zone B", etc.
                expected_zone_format = f"Zone {zone_letter}"
                if zones_str != expected_zone_format:
                    _LOGGER.debug("Skipping vacation '%s' with zones '%s' (looking for '%s')", record.get('description', 'N/A'), zones_str, expected_zone_format)
                    continue

                # If academy is specified, filter by location (academy name)
                if self.academy and location_str and location_str != self.academy:
                    _LOGGER.debug("Skipping vacation '%s' with location '%s' (looking for '%s')", record.get('description', 'N/A'), location_str, self.academy)
                    continue

                vacance = {
                    "name": record.get("description", ""),
                    "start": datetime.fromisoformat(record.get("start_date", "")).date(),
                    "end": datetime.fromisoformat(record.get("end_date", "")).date(),
                    "zones": [zones_str],
                    "academy": location_str if location_str else self.academy,
                    "timezone": self.timezone_str,
                }
                self._vacances.append(vacance)
                _LOGGER.debug("Added vacation: %s (%s to %s) for zone %s, academy %s", vacance['name'], vacance['start'], vacance['end'], zones_str, location_str)
            except (ValueError, KeyError, TypeError) as e:
                _LOGGER.debug("Failed to parse vacation record: %s, error: %s", record.get('description', 'N/A'), e)
                continue

        if not self._vacances:
            _LOGGER.warning("No vacations found for Zone %s (%s), Academy %s in API response, loading static data", self.zone, zone_letter, self.academy)
        else:
            self._vacances.sort(key=lambda x: x["start"])
            _LOGGER.info("Successfully parsed %d vacations for Zone %s, Academy %s", len(self._vacances), self.zone, self.academy)
    def get_vacances_en_cours(self) -> Optional[dict]:
        """Get current school holidays if any.

        Uses binary search for O(log n) performance since _vacances is sorted by start date.
        Uses timezone-aware date for DOM-TOM.
        """
        if not self._vacances:
            return None

        # Utiliser la date actuelle dans le fuseau horaire de la zone
        today = datetime.now(self.timezone).date()

        # Binary search to find the vacation period containing today
        # We need to find a vacation where start <= today <= end

        # First, use bisect to find insertion point for today
        # This gives us a hint about where to look
        start_dates = [v["start"] for v in self._vacances]
        idx = bisect.bisect_right(start_dates, today)

        # Check the vacation period just before the insertion point
        # (the one that starts at or before today)
        if idx > 0:
            vacances = self._vacances[idx - 1]
            if vacances["start"] <= today <= vacances["end"]:
                return vacances

        # Also check the vacation at the insertion point in case
        # we're exactly at the start date
        if idx < len(self._vacances):
            vacances = self._vacances[idx]
            if vacances["start"] <= today <= vacances["end"]:
                return vacances

        return None

    def get_prochaines_vacances(self) -> Optional[dict]:
        """Get next school holidays.

        Uses binary search for O(log n) performance since _vacances is sorted by start date.
        Uses timezone-aware date for DOM-TOM.
        """
        if not self._vacances:
            return None

        # Utiliser la date actuelle dans le fuseau horaire de la zone
        today = datetime.now(self.timezone).date()

        # Binary search to find the first vacation that starts after today
        start_dates = [v["start"] for v in self._vacances]
        idx = bisect.bisect_right(start_dates, today)

        # bisect_right returns the insertion point, which is the index
        # of the first vacation that starts after today
        if idx < len(self._vacances):
            return self._vacances[idx]

        return None

    def get_jours_avant_vacances(self) -> Optional[int]:
        """Get days until next school holidays with timezone awareness."""
        prochaines = self.get_prochaines_vacances()
        if prochaines:
            today = datetime.now(self.timezone).date()
            delta = prochaines["start"] - today
            return delta.days
        return None

    def get_jours_restants_vacances(self) -> Optional[int]:
        """Get remaining days of current school holidays with timezone awareness."""
        vacances_en_cours = self.get_vacances_en_cours()
        if vacances_en_cours:
            today = datetime.now(self.timezone).date()
            delta = vacances_en_cours["end"] - today
            return max(0, delta.days + 1)  # +1 pour inclure le dernier jour
        return None

    def get_all_vacances_for_calendar(self) -> list[dict]:
        """Get all vacances periods for calendar entity."""
        return self._vacances.copy()

    def is_vacation_period(self) -> bool:
        """Check if we're currently in a vacation period."""
        return self.get_vacances_en_cours() is not None

