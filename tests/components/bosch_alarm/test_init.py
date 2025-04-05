"""Tests for bosch alarm integration init."""

from unittest.mock import AsyncMock, patch

import pytest

from homeassistant.config_entries import ConfigEntryState
from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry as dr, entity_registry as er
from homeassistant.setup import async_setup_component

from . import setup_integration

from tests.common import MockConfigEntry
from tests.typing import WebSocketGenerator


@pytest.fixture
def disable_platform_only():
    """Disable platforms to speed up tests."""
    with patch("homeassistant.components.bosch_alarm.PLATFORMS", []):
        yield


@pytest.mark.parametrize("model", ["solution_3000"])
@pytest.mark.parametrize("exception", [PermissionError(), TimeoutError()])
async def test_incorrect_auth(
    disable_platform_only: None,
    hass: HomeAssistant,
    mock_panel: AsyncMock,
    mock_config_entry: MockConfigEntry,
    exception: Exception,
) -> None:
    """Test errors with incorrect auth."""
    mock_panel.connect.side_effect = exception
    await setup_integration(hass, mock_config_entry)
    assert mock_config_entry.state is ConfigEntryState.SETUP_RETRY


async def test_device_remove_devices(
    hass: HomeAssistant,
    hass_ws_client: WebSocketGenerator,
    device_registry: dr.DeviceRegistry,
    entity_registry: er.EntityRegistry,
    mock_panel: AsyncMock,
    mock_config_entry: MockConfigEntry,
) -> None:
    """Test we can remove a device."""
    assert await async_setup_component(hass, "config", {})
    await setup_integration(hass, mock_config_entry)

    entity = entity_registry.entities["alarm_control_panel.area1"]

    device_entry = device_registry.async_get(entity.device_id)
    client = await hass_ws_client(hass)
    response = await client.remove_device(device_entry.id, mock_config_entry.entry_id)
    assert response["success"]
