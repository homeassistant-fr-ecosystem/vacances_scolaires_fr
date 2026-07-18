"""Shared fixtures for vacances_scolaires_fr tests."""

from datetime import date
from typing import Any

import pytest

from custom_components.vacances_scolaires_fr.api import VacancesScolairesAPI

ZONE = "A"
ACADEMY = "Besançon"

MOCK_API_RESPONSE: dict[str, Any] = {
    "results": [
        {
            "description": "Vacances de la Toussaint",
            "start_date": "2025-10-18T00:00:00+00:00",
            "end_date": "2025-11-03T00:00:00+00:00",
            "zones": "Zone A",
            "location": "Besançon",
            "population": "Élèves",
        },
        {
            "description": "Vacances de Noël",
            "start_date": "2025-12-20T00:00:00+00:00",
            "end_date": "2026-01-05T00:00:00+00:00",
            "zones": "Zone A",
            "location": "Besançon",
            "population": "-",
        },
        {
            "description": "Vacances d'hiver",
            "start_date": "2026-02-07T00:00:00+00:00",
            "end_date": "2026-02-23T00:00:00+00:00",
            "zones": "Zone A",
            "location": "Besançon",
            "population": "Élèves",
        },
    ]
}

MOCK_VACANCES: list[dict[str, Any]] = [
    {
        "name": "Vacances de la Toussaint",
        "start": date(2025, 10, 18),
        "end": date(2025, 11, 3),
        "zones": ["Zone A"],
        "academy": "Besançon",
        "timezone": "Europe/Paris",
    },
    {
        "name": "Vacances de Noël",
        "start": date(2025, 12, 20),
        "end": date(2026, 1, 5),
        "zones": ["Zone A"],
        "academy": "Besançon",
        "timezone": "Europe/Paris",
    },
    {
        "name": "Vacances d'hiver",
        "start": date(2026, 2, 7),
        "end": date(2026, 2, 23),
        "zones": ["Zone A"],
        "academy": "Besançon",
        "timezone": "Europe/Paris",
    },
]


@pytest.fixture
def api() -> VacancesScolairesAPI:
    """Return a VacancesScolairesAPI instance with no cache dir."""
    return VacancesScolairesAPI(ZONE, ACADEMY)


@pytest.fixture
def api_with_vacances() -> VacancesScolairesAPI:
    """Return an API instance pre-loaded with vacation data."""
    instance = VacancesScolairesAPI(ZONE, ACADEMY)
    instance._vacances = list(MOCK_VACANCES)
    instance._use_static_data = False
    return instance
