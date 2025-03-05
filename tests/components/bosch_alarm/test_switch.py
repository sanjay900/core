"""Tests for Bosch Alarm component."""

from collections.abc import AsyncGenerator
from unittest.mock import patch

import pytest
from syrupy.assertion import SnapshotAssertion

from homeassistant.components.switch import DOMAIN as SWITCH_DOMAIN
from homeassistant.const import ATTR_ENTITY_ID, STATE_OFF, STATE_ON, Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er

from .conftest import MockBoschAlarmConfig

from tests.common import MockConfigEntry, snapshot_platform


@pytest.fixture(autouse=True)
async def platforms() -> AsyncGenerator[None]:
    """Return the platforms to be loaded for this test."""
    with patch("homeassistant.components.bosch_alarm.PLATFORMS", [Platform.SWITCH]):
        yield


@pytest.mark.parametrize(
    "bosch_alarm_test_data",
    ["Solution 3000"],
    indirect=True,
)
async def test_update_switch_device(
    hass: HomeAssistant,
    bosch_alarm_test_data: MockBoschAlarmConfig,
    bosch_config_entry: MockConfigEntry,
) -> None:
    """Test that alarm panel state changes after arming the panel."""
    bosch_config_entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(bosch_config_entry.entry_id)
    await hass.async_block_till_done()
    entity_id = "switch.bosch_solution_3000_output_a"
    assert hass.states.get(entity_id).state == STATE_OFF
    await hass.services.async_call(
        SWITCH_DOMAIN,
        "turn_on",
        {ATTR_ENTITY_ID: entity_id},
        blocking=True,
    )
    await hass.async_block_till_done()
    assert hass.states.get(entity_id).state == STATE_ON


@pytest.mark.parametrize(
    "bosch_alarm_test_data",
    [
        "Solution 3000",
        "AMAX 3000",
        "B5512 (US1B)",
    ],
    indirect=True,
)
async def test_switch(
    hass: HomeAssistant,
    entity_registry: er.EntityRegistry,
    snapshot: SnapshotAssertion,
    bosch_config_entry: MockConfigEntry,
) -> None:
    """Test the switch state."""
    bosch_config_entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(bosch_config_entry.entry_id)
    await hass.async_block_till_done()

    await snapshot_platform(
        hass, entity_registry, snapshot, bosch_config_entry.entry_id
    )
