"""Support for Bosch Alarm Panel outputs as switches."""

from __future__ import annotations

from typing import Any

from homeassistant.components.switch import SwitchEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import BoschAlarmConfigEntry, BoschAlarmCoordinator


async def async_setup_entry(
    hass: HomeAssistant | None,
    config_entry: BoschAlarmConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up switch entities for outputs."""

    coordinator: BoschAlarmCoordinator = config_entry.runtime_data

    async_add_entities(
        PanelOutputEntity(coordinator, output_id)
        for output_id in coordinator.panel.outputs
    )


PARALLEL_UPDATES = 0


class PanelOutputEntity(CoordinatorEntity[BoschAlarmCoordinator], SwitchEntity):
    """An output entity for a bosch alarm panel."""

    _attr_has_entity_name = True

    def __init__(self, coordinator: BoschAlarmCoordinator, output_id: int) -> None:
        """Set up an output entity for a bosch alarm panel."""
        super().__init__(coordinator, output_id)
        self._output = coordinator.panel.outputs[output_id]
        self._output_id = output_id
        self._attr_name = self._output.name
        self._observer = self._output.status_observer
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, coordinator.config_entry.entry_id)},
            name=f"Bosch {coordinator.panel.model}",
            manufacturer="Bosch Security Systems",
            model=coordinator.panel.model,
            sw_version=coordinator.panel.firmware_version,
        )
        self._attr_unique_id = f"{coordinator.config_entry.entry_id}_output_{output_id}"

    async def async_added_to_hass(self) -> None:
        """Observe state changes."""
        await super().async_added_to_hass()
        self._observer.attach(self.schedule_update_ha_state)

    async def async_will_remove_from_hass(self) -> None:
        """Stop observing state changes."""
        self._observer.detach(self.schedule_update_ha_state)

    @property
    def is_on(self) -> bool:
        """Check if this entity is on."""
        return self._output.is_active()

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn on this output."""
        await self.coordinator.panel.set_output_active(self._output_id)

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn off this output."""
        await self.coordinator.panel.set_output_inactive(self._output_id)
