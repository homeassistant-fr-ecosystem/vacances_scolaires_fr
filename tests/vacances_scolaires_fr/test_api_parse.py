"""Tests for VacancesScolairesAPI parsing and query logic."""

from contextlib import contextmanager
from datetime import date, datetime
from typing import Any, Generator
from unittest.mock import patch
from zoneinfo import ZoneInfo

import pytest

from custom_components.vacances_scolaires_fr.api import VacancesScolairesAPI

from .conftest import ACADEMY, MOCK_API_RESPONSE, ZONE


@contextmanager
def freeze_today(d: date) -> Generator[None, None, None]:
    """Patch datetime.now in the api module so .date() returns d."""

    class _FakeDatetime(datetime):
        @classmethod
        def now(cls, tz: Any = None) -> "_FakeDatetime":  # type: ignore[override]
            return cls(d.year, d.month, d.day, tzinfo=tz or ZoneInfo("Europe/Paris"))

    with patch("custom_components.vacances_scolaires_fr.api.datetime", _FakeDatetime):
        yield


class TestConstructor:
    def test_valid_zone_and_academy(self) -> None:
        api = VacancesScolairesAPI(ZONE, ACADEMY)
        assert api.zone == ZONE
        assert api.academy == ACADEMY

    def test_invalid_zone_raises(self) -> None:
        with pytest.raises(ValueError, match="Invalid zone"):
            VacancesScolairesAPI("Z")

    def test_invalid_academy_raises(self) -> None:
        with pytest.raises(ValueError, match="Invalid academy"):
            VacancesScolairesAPI(ZONE, "NotAnAcademy")

    def test_default_academy_when_none_provided(self) -> None:
        api = VacancesScolairesAPI(ZONE)
        assert api.academy != ""

    def test_domtom_zone(self) -> None:
        api = VacancesScolairesAPI("Guadeloupe")
        assert api.zone == "Guadeloupe"

    def test_custom_timezone(self) -> None:
        api = VacancesScolairesAPI(ZONE, ACADEMY, custom_timezone="America/Martinique")
        assert api.timezone_str == "America/Martinique"

    def test_invalid_timezone_falls_back(self) -> None:
        api = VacancesScolairesAPI(ZONE, ACADEMY, custom_timezone="Not/ATimezone")
        assert api.timezone_str == "Europe/Paris"

    def test_no_cache_dir_when_no_path(self) -> None:
        api = VacancesScolairesAPI(ZONE, ACADEMY)
        assert api._cache_dir is None

    def test_cache_dir_set_when_path_provided(self, tmp_path: Any) -> None:
        api = VacancesScolairesAPI(ZONE, ACADEMY, hass_config_path=str(tmp_path))
        assert api._cache_dir is not None
        assert "vacances_scolaires_fr" in api._cache_dir


class TestParseApiData:
    def test_parses_valid_response(self, api: VacancesScolairesAPI) -> None:
        api._parse_api_data(MOCK_API_RESPONSE)
        assert len(api._vacances) == 3

    def test_parses_vacation_fields(self, api: VacancesScolairesAPI) -> None:
        api._parse_api_data(MOCK_API_RESPONSE)
        first = api._vacances[0]
        assert first["name"] == "Vacances de la Toussaint"
        assert first["start"] == date(2025, 10, 18)
        assert first["end"] == date(2025, 11, 3)
        assert first["academy"] == "Besançon"

    def test_filters_teacher_population(self, api: VacancesScolairesAPI) -> None:
        data: dict[str, Any] = {
            "results": [
                {
                    "description": "Congé enseignants",
                    "start_date": "2025-10-18T00:00:00+00:00",
                    "end_date": "2025-10-25T00:00:00+00:00",
                    "zones": "Zone A",
                    "location": "Besançon",
                    "population": "Enseignants",
                }
            ]
        }
        api._parse_api_data(data)
        assert api._vacances == []

    def test_keeps_all_population_marker(self, api: VacancesScolairesAPI) -> None:
        data: dict[str, Any] = {
            "results": [
                {
                    "description": "Vacances communes",
                    "start_date": "2025-12-20T00:00:00+00:00",
                    "end_date": "2026-01-05T00:00:00+00:00",
                    "zones": "Zone A",
                    "location": "Besançon",
                    "population": "-",
                }
            ]
        }
        api._parse_api_data(data)
        assert len(api._vacances) == 1

    def test_filters_wrong_zone(self, api: VacancesScolairesAPI) -> None:
        data: dict[str, Any] = {
            "results": [
                {
                    "description": "Vacances Zone B",
                    "start_date": "2025-10-18T00:00:00+00:00",
                    "end_date": "2025-10-25T00:00:00+00:00",
                    "zones": "Zone B",
                    "location": "Besançon",
                    "population": "Élèves",
                }
            ]
        }
        api._parse_api_data(data)
        assert api._vacances == []

    def test_filters_wrong_academy(self, api: VacancesScolairesAPI) -> None:
        data: dict[str, Any] = {
            "results": [
                {
                    "description": "Vacances",
                    "start_date": "2025-10-18T00:00:00+00:00",
                    "end_date": "2025-10-25T00:00:00+00:00",
                    "zones": "Zone A",
                    "location": "Paris",
                    "population": "Élèves",
                }
            ]
        }
        api._parse_api_data(data)
        assert api._vacances == []

    def test_empty_results_loads_static_data(self, api: VacancesScolairesAPI) -> None:
        api._parse_api_data({"results": []})
        assert api._vacances == []
        assert api._use_static_data is True

    def test_missing_results_key_loads_static_data(
        self, api: VacancesScolairesAPI
    ) -> None:
        api._parse_api_data({"other_key": []})
        assert api._use_static_data is True

    def test_invalid_date_skips_record(self, api: VacancesScolairesAPI) -> None:
        data: dict[str, Any] = {
            "results": [
                {
                    "description": "Bad date",
                    "start_date": "not-a-date",
                    "end_date": "2025-10-25T00:00:00+00:00",
                    "zones": "Zone A",
                    "location": "Besançon",
                    "population": "Élèves",
                },
                {
                    "description": "Good one",
                    "start_date": "2025-10-18T00:00:00+00:00",
                    "end_date": "2025-11-03T00:00:00+00:00",
                    "zones": "Zone A",
                    "location": "Besançon",
                    "population": "Élèves",
                },
            ]
        }
        api._parse_api_data(data)
        assert len(api._vacances) == 1
        assert api._vacances[0]["name"] == "Good one"

    def test_results_sorted_by_start(self, api: VacancesScolairesAPI) -> None:
        data: dict[str, Any] = {
            "results": [
                {
                    "description": "Second",
                    "start_date": "2025-12-20T00:00:00+00:00",
                    "end_date": "2026-01-05T00:00:00+00:00",
                    "zones": "Zone A",
                    "location": "Besançon",
                    "population": "Élèves",
                },
                {
                    "description": "First",
                    "start_date": "2025-10-18T00:00:00+00:00",
                    "end_date": "2025-11-03T00:00:00+00:00",
                    "zones": "Zone A",
                    "location": "Besançon",
                    "population": "Élèves",
                },
            ]
        }
        api._parse_api_data(data)
        assert api._vacances[0]["name"] == "First"
        assert api._vacances[1]["name"] == "Second"


class TestGetVacancesEnCours:
    def test_returns_none_when_no_vacances(self, api: VacancesScolairesAPI) -> None:
        assert api.get_vacances_en_cours() is None

    def test_returns_current_vacation(
        self, api_with_vacances: VacancesScolairesAPI
    ) -> None:
        with freeze_today(date(2025, 10, 25)):
            result = api_with_vacances.get_vacances_en_cours()
        assert result is not None
        assert result["name"] == "Vacances de la Toussaint"

    def test_returns_none_outside_vacation(
        self, api_with_vacances: VacancesScolairesAPI
    ) -> None:
        with freeze_today(date(2025, 11, 15)):
            result = api_with_vacances.get_vacances_en_cours()
        assert result is None

    def test_includes_first_day(self, api_with_vacances: VacancesScolairesAPI) -> None:
        with freeze_today(date(2025, 10, 18)):
            result = api_with_vacances.get_vacances_en_cours()
        assert result is not None

    def test_includes_last_day(self, api_with_vacances: VacancesScolairesAPI) -> None:
        with freeze_today(date(2025, 11, 3)):
            result = api_with_vacances.get_vacances_en_cours()
        assert result is not None


class TestGetProchinesVacances:
    def test_returns_none_when_no_vacances(self, api: VacancesScolairesAPI) -> None:
        assert api.get_prochaines_vacances() is None

    def test_returns_next_vacation_when_before_all(
        self, api_with_vacances: VacancesScolairesAPI
    ) -> None:
        with freeze_today(date(2025, 9, 1)):
            result = api_with_vacances.get_prochaines_vacances()
        assert result is not None
        assert result["name"] == "Vacances de la Toussaint"

    def test_returns_next_vacation_after_current(
        self, api_with_vacances: VacancesScolairesAPI
    ) -> None:
        # During Toussaint, next should be Noël
        with freeze_today(date(2025, 10, 25)):
            result = api_with_vacances.get_prochaines_vacances()
        assert result is not None
        assert result["name"] == "Vacances de Noël"

    def test_returns_none_after_last_vacation(
        self, api_with_vacances: VacancesScolairesAPI
    ) -> None:
        with freeze_today(date(2026, 3, 1)):
            result = api_with_vacances.get_prochaines_vacances()
        assert result is None


class TestGetJoursAvantVacances:
    def test_returns_none_when_no_vacances(self, api: VacancesScolairesAPI) -> None:
        assert api.get_jours_avant_vacances() is None

    def test_returns_days_until_next(
        self, api_with_vacances: VacancesScolairesAPI
    ) -> None:
        # Oct 1 → Toussaint starts Oct 18 → 17 days
        with freeze_today(date(2025, 10, 1)):
            result = api_with_vacances.get_jours_avant_vacances()
        assert result == 17


class TestGetJoursRestantsVacances:
    def test_returns_none_when_not_in_vacation(
        self, api_with_vacances: VacancesScolairesAPI
    ) -> None:
        with freeze_today(date(2025, 11, 15)):
            result = api_with_vacances.get_jours_restants_vacances()
        assert result is None

    def test_returns_days_remaining_in_vacation(
        self, api_with_vacances: VacancesScolairesAPI
    ) -> None:
        # Toussaint ends Nov 3. On Oct 30, 5 days remain (Oct 30,31, Nov 1,2,3)
        with freeze_today(date(2025, 10, 30)):
            result = api_with_vacances.get_jours_restants_vacances()
        assert result == 5

    def test_returns_one_on_last_day(
        self, api_with_vacances: VacancesScolairesAPI
    ) -> None:
        with freeze_today(date(2025, 11, 3)):
            result = api_with_vacances.get_jours_restants_vacances()
        assert result == 1


class TestIsVacationPeriod:
    def test_false_outside_vacation(
        self, api_with_vacances: VacancesScolairesAPI
    ) -> None:
        with freeze_today(date(2025, 11, 15)):
            assert api_with_vacances.is_vacation_period() is False

    def test_true_during_vacation(
        self, api_with_vacances: VacancesScolairesAPI
    ) -> None:
        with freeze_today(date(2025, 10, 25)):
            assert api_with_vacances.is_vacation_period() is True


class TestGetAllVacancesForCalendar:
    def test_returns_copy_of_vacances(
        self, api_with_vacances: VacancesScolairesAPI
    ) -> None:
        result = api_with_vacances.get_all_vacances_for_calendar()
        assert result is not api_with_vacances._vacances
        assert len(result) == 3

    def test_returns_empty_list_when_no_data(self, api: VacancesScolairesAPI) -> None:
        assert api.get_all_vacances_for_calendar() == []
