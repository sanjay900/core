"""Tests for Bosch Alarm component."""

from collections.abc import AsyncGenerator
from unittest.mock import patch

import pytest

from homeassistant.components.bosch_alarm.const import (
    ATTR_CONFIG_ENTRY_ID,
    DATETIME_ATTR,
    DOMAIN,
    SET_DATE_TIME_SERVICE_NAME,
)
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.util import dt as dt_util

from .conftest import MockBoschAlarmConfig

from tests.common import MockConfigEntry


@pytest.fixture(autouse=True)
async def platforms() -> AsyncGenerator[None]:
    """Return the platforms to be loaded for this test."""
    with patch("homeassistant.components.bosch_alarm.PLATFORMS", []):
        yield


@pytest.mark.parametrize(
    ("bosch_alarm_test_data", "bosch_config_entry"),
    [("Solution 3000", None)],
    indirect=True,
)
async def test_set_date_time_service(
    hass: HomeAssistant,
    bosch_alarm_test_data: MockBoschAlarmConfig,
    bosch_config_entry: MockConfigEntry,
) -> None:
    """Test that alarm panel state changes after arming the panel."""
    bosch_config_entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(bosch_config_entry.entry_id)
    await hass.async_block_till_done()
    await hass.services.async_call(
        DOMAIN,
        SET_DATE_TIME_SERVICE_NAME,
        {
            ATTR_CONFIG_ENTRY_ID: [bosch_config_entry.entry_id],
            DATETIME_ATTR: dt_util.now(),
        },
        blocking=True,
    )

    with pytest.raises(HomeAssistantError):
        await hass.services.async_call(
            DOMAIN,
            SET_DATE_TIME_SERVICE_NAME,
            {
                ATTR_CONFIG_ENTRY_ID: ["bad-config_id"],
                DATETIME_ATTR: dt_util.now(),
            },
            blocking=True,
        )
