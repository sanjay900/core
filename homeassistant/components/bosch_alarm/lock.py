"""Support for Bosch Alarm Panel doors as locks."""

from __future__ import annotations

from typing import Any

from homeassistant.components.lock import LockEntity
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
    """Set up lock entities for each door."""

    coordinator: BoschAlarmCoordinator = config_entry.runtime_data

    async_add_entities(
        PanelLockEntity(coordinator, door_id) for door_id in coordinator.panel.doors
    )


class PanelLockEntity(CoordinatorEntity[BoschAlarmCoordinator], LockEntity):
    """A lock entity for a door on a bosch alarm panel."""

    _attr_has_entity_name = True

    def __init__(self, coordinator: BoschAlarmCoordinator, door_id: int) -> None:
        """Set up a lock entity for a door on a bosch alarm panel."""
        super().__init__(coordinator, door_id)
        self._door = coordinator.panel.doors[door_id]
        self._attr_name = self._door.name
        self._attr_unique_id = f"{coordinator.config_entry.entry_id}_door_{door_id}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, coordinator.config_entry.entry_id)},
            name=f"Bosch {coordinator.panel.model}",
            manufacturer="Bosch Security Systems",
            model=coordinator.panel.model,
            sw_version=coordinator.panel.firmware_version,
        )
        self._door_id = door_id

    @property
    def is_locked(self) -> bool:
        """Return if the door is locked."""
        return self._door.is_locked()

    @property
    def available(self) -> bool:
        """Return if the door is available."""
        return self._door.is_open() or self._door.is_locked()

    async def async_lock(self, **kwargs: Any) -> None:
        """Lock the door."""
        await self.coordinator.panel.door_relock(self._door_id)

    async def async_unlock(self, **kwargs: Any) -> None:
        """Unlock the door."""
        await self.coordinator.panel.door_unlock(self._door_id)

    async def async_added_to_hass(self) -> None:
        """Observe state changes."""
        await super().async_added_to_hass()
        self._door.status_observer.attach(self.schedule_update_ha_state)

    async def async_will_remove_from_hass(self) -> None:
        """Stop observing state changes."""
        self._door.status_observer.detach(self.schedule_update_ha_state)
