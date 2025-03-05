"""Tests for Bosch Alarm component."""

from collections.abc import AsyncGenerator
from unittest.mock import patch

import pytest
from syrupy.assertion import SnapshotAssertion

from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er

from tests.common import MockConfigEntry, snapshot_platform


@pytest.fixture(autouse=True)
async def platforms() -> AsyncGenerator[None]:
    """Return the platforms to be loaded for this test."""
    with patch("homeassistant.components.bosch_alarm.PLATFORMS", [Platform.SENSOR]):
        yield


@pytest.mark.parametrize(
    "bosch_alarm_test_data",
    [
        "Solution 3000",
        "AMAX 3000",
        "B5512 (US1B)",
    ],
    indirect=True,
)
async def test_sensor(
    hass: HomeAssistant,
    entity_registry: er.EntityRegistry,
    snapshot: SnapshotAssertion,
    bosch_config_entry: MockConfigEntry,
) -> None:
    """Test the sensor state."""
    bosch_config_entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(bosch_config_entry.entry_id)
    await hass.async_block_till_done()

    await snapshot_platform(
        hass, entity_registry, snapshot, bosch_config_entry.entry_id
    )
