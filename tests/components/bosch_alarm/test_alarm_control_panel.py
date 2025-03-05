"""Tests for Bosch Alarm component."""

import asyncio
from collections.abc import AsyncGenerator
from unittest.mock import patch

import pytest
from syrupy.assertion import SnapshotAssertion

from homeassistant.components.alarm_control_panel import (
    DOMAIN as ALARM_DOMAIN,
    AlarmControlPanelState,
)
from homeassistant.const import ATTR_CODE, ATTR_ENTITY_ID, Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er

from .conftest import MockBoschAlarmConfig

from tests.common import MockConfigEntry, snapshot_platform


@pytest.fixture(autouse=True)
async def platforms() -> AsyncGenerator[None]:
    """Return the platforms to be loaded for this test."""
    with patch(
        "homeassistant.components.bosch_alarm.PLATFORMS", [Platform.ALARM_CONTROL_PANEL]
    ):
        yield


@pytest.mark.parametrize(
    ("bosch_alarm_test_data", "bosch_config_entry"),
    [
        ("Solution 3000", None),
        ("AMAX 3000", None),
        ("B5512 (US1B)", None),
    ],
    indirect=True,
)
async def test_alarm_control_panel(
    hass: HomeAssistant,
    entity_registry: er.EntityRegistry,
    snapshot: SnapshotAssertion,
    bosch_config_entry: MockConfigEntry,
) -> None:
    """Test the alarm_control_panel state."""
    bosch_config_entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(bosch_config_entry.entry_id)
    await hass.async_block_till_done()

    await snapshot_platform(
        hass, entity_registry, snapshot, bosch_config_entry.entry_id
    )


@pytest.mark.parametrize(
    ("bosch_alarm_test_data", "bosch_config_entry"),
    [("Solution 3000", None)],
    indirect=True,
)
async def test_update_alarm_device(
    hass: HomeAssistant,
    bosch_alarm_test_data: MockBoschAlarmConfig,
    bosch_config_entry: MockConfigEntry,
) -> None:
    """Test that alarm panel state changes after arming the panel."""
    bosch_config_entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(bosch_config_entry.entry_id)
    await hass.async_block_till_done()
    entity_id = "alarm_control_panel.bosch_solution_3000_area1"
    assert hass.states.get(entity_id).state == AlarmControlPanelState.DISARMED
    await hass.services.async_call(
        ALARM_DOMAIN,
        "alarm_arm_away",
        {ATTR_ENTITY_ID: entity_id},
        blocking=True,
    )
    await hass.async_block_till_done()
    assert hass.states.get(entity_id).state == AlarmControlPanelState.ARMING
    await asyncio.sleep(0.1)
    assert hass.states.get(entity_id).state == AlarmControlPanelState.ARMED_AWAY
    await hass.services.async_call(
        ALARM_DOMAIN,
        "alarm_disarm",
        {ATTR_ENTITY_ID: entity_id},
        blocking=True,
    )
    await hass.async_block_till_done()
    assert hass.states.get(entity_id).state == AlarmControlPanelState.DISARMED
    await hass.services.async_call(
        ALARM_DOMAIN,
        "alarm_arm_home",
        {ATTR_ENTITY_ID: entity_id},
        blocking=True,
    )
    await hass.async_block_till_done()
    assert hass.states.get(entity_id).state == AlarmControlPanelState.ARMING
    await asyncio.sleep(0.1)
    assert hass.states.get(entity_id).state == AlarmControlPanelState.ARMED_HOME
    await hass.services.async_call(
        ALARM_DOMAIN,
        "alarm_disarm",
        {ATTR_ENTITY_ID: entity_id},
        blocking=True,
    )
    await hass.async_block_till_done()
    assert hass.states.get(entity_id).state == AlarmControlPanelState.DISARMED


@pytest.mark.parametrize(
    ("bosch_alarm_test_data", "bosch_config_entry"),
    [("Solution 3000", "1234"), ("Solution 3000", "abcdef")],
    indirect=True,
)
async def test_update_alarm_device_with_incorrect_code(
    hass: HomeAssistant,
    bosch_alarm_test_data: MockBoschAlarmConfig,
    bosch_config_entry: MockConfigEntry,
) -> None:
    """Test that alarm panel state does not change if a panel is armed with the wrong code."""
    bosch_config_entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(bosch_config_entry.entry_id)
    await hass.async_block_till_done()
    entity_id = "alarm_control_panel.bosch_solution_3000_area1"
    assert hass.states.get(entity_id).state == AlarmControlPanelState.DISARMED
    await hass.services.async_call(
        ALARM_DOMAIN,
        "alarm_arm_away",
        {ATTR_ENTITY_ID: entity_id, ATTR_CODE: "12345"},
        blocking=True,
    )
    await hass.async_block_till_done()
    assert hass.states.get(entity_id).state == AlarmControlPanelState.DISARMED


@pytest.mark.parametrize(
    ("bosch_alarm_test_data", "bosch_config_entry"),
    [("Solution 3000", "12345"), ("Solution 3000", "abcdef")],
    indirect=True,
)
async def test_update_alarm_device_with_code(
    hass: HomeAssistant,
    bosch_alarm_test_data: MockBoschAlarmConfig,
    bosch_config_entry: MockConfigEntry,
) -> None:
    """Test that alarm panel state changes after arming the panel with a code."""
    bosch_config_entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(bosch_config_entry.entry_id)
    await hass.async_block_till_done()
    entity_id = "alarm_control_panel.bosch_solution_3000_area1"
    assert hass.states.get(entity_id).state == AlarmControlPanelState.DISARMED
    await hass.services.async_call(
        ALARM_DOMAIN,
        "alarm_arm_away",
        {ATTR_ENTITY_ID: entity_id, ATTR_CODE: bosch_config_entry.options[ATTR_CODE]},
        blocking=True,
    )
    await hass.async_block_till_done()
    assert hass.states.get(entity_id).state == AlarmControlPanelState.ARMING
    await asyncio.sleep(0.1)
    assert hass.states.get(entity_id).state == AlarmControlPanelState.ARMED_AWAY
