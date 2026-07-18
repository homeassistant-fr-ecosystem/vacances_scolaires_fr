"""Top-level pytest configuration for vacances_scolaires_fr tests."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

pytest_plugins = "pytest_homeassistant_custom_component"


@pytest.fixture(autouse=True)
def enable_custom_integrations(enable_custom_integrations):  # noqa: ARG001
    """Enable custom integrations for all tests."""
    return
