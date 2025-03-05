"""Tests for bosch alarm integration init."""

from unittest.mock import patch

import pytest

from homeassistant.core import HomeAssistant

from .conftest import MockBoschAlarmConfig

from tests.common import MockConfigEntry


@pytest.fixture(autouse=True)
def disable_platform_only():
    """Disable platforms to speed up tests."""
    with patch("homeassistant.components.bosch_alarm.PLATFORMS", []):
        yield


@pytest.mark.parametrize(
    ("bosch_alarm_test_data", "bosch_config_entry", "exception"),
    [
        ("Solution 3000", None, PermissionError()),
        ("Solution 3000", None, TimeoutError()),
    ],
    indirect=["bosch_alarm_test_data", "bosch_config_entry"],
)
async def test_init_exceptions(
    hass: HomeAssistant,
    bosch_alarm_test_data: MockBoschAlarmConfig,
    bosch_config_entry: MockConfigEntry,
    exception: Exception,
) -> None:
    """Test errors with incorrect auth."""
    bosch_alarm_test_data.side_effect = exception
    bosch_config_entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(bosch_config_entry.entry_id) is False
