"""Support for Bosch Alarm Panel binary sensors."""

from __future__ import annotations

import re

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
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
    """Set up binary sensors for alarm points and the connection status."""
    coordinator: BoschAlarmCoordinator = config_entry.runtime_data

    async_add_entities([ConnectionStatusSensor(coordinator)])

    async_add_entities(
        PointSensor(coordinator, point_id) for point_id in coordinator.panel.points
    )


def _guess_device_class(name):
    if re.search(r"\b(win(d)?(ow)?|wn)\b", name):
        return BinarySensorDeviceClass.WINDOW
    if re.search(r"\b(door|dr)\b", name):
        return BinarySensorDeviceClass.DOOR
    if re.search(r"\b(motion|md)\b", name):
        return BinarySensorDeviceClass.MOTION
    if re.search(r"\bco\b", name):
        return BinarySensorDeviceClass.CO
    if re.search(r"\bsmoke\b", name):
        return BinarySensorDeviceClass.SMOKE
    if re.search(r"\bglassbr(ea)?k\b", name):
        return BinarySensorDeviceClass.TAMPER
    return None


class PointSensor(CoordinatorEntity[BoschAlarmCoordinator], BinarySensorEntity):
    """A binary sensor entity for a point in a bosch alarm panel."""

    _attr_has_entity_name = True

    def __init__(self, coordinator: BoschAlarmCoordinator, point_id: int) -> None:
        """Set up a binary sensor entity for a point in a bosch alarm panel."""
        super().__init__(coordinator, point_id)
        self._attr_unique_id = f"{coordinator.config_entry.entry_id}_point_{point_id}"
        self._point = coordinator.panel.points[point_id]
        self._attr_name = self._point.name
        self._attr_should_poll = False
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, coordinator.config_entry.entry_id)},
            name=f"Bosch {coordinator.panel.model}",
            manufacturer="Bosch Security Systems",
            model=coordinator.panel.model,
            sw_version=coordinator.panel.firmware_version,
        )

    @property
    def is_on(self) -> bool:
        """Return if this point sensor is on."""
        return self._point.is_open()

    @property
    def available(self) -> bool:
        """Return if this point sensor is available."""
        return self._point.is_open() or self._point.is_normal()

    @property
    def device_class(self) -> BinarySensorDeviceClass:
        """Return a guess for the device class for this point sensor."""
        return _guess_device_class(self._point.name.lower())

    async def async_added_to_hass(self) -> None:
        """Run when entity attached to hass."""
        await super().async_added_to_hass()
        self._point.status_observer.attach(self.schedule_update_ha_state)

    async def async_will_remove_from_hass(self) -> None:
        """Set the date and time on a bosch alarm panel."""
        self._point.status_observer.detach(self.schedule_update_ha_state)


class ConnectionStatusSensor(
    CoordinatorEntity[BoschAlarmCoordinator], BinarySensorEntity
):
    """A binary sensor entity for the connection status in a bosch alarm panel."""

    _attr_has_entity_name = True

    def __init__(self, coordinator) -> None:
        """Set up a binary sensor entity for the connection status in a bosch alarm panel."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.config_entry.entry_id}_connection_status"
        self._attr_name = "Connection Status"
        self._attr_should_poll = False
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, coordinator.config_entry.entry_id)},
            name=f"Bosch {coordinator.panel.model}",
            manufacturer="Bosch Security Systems",
            model=coordinator.panel.model,
            sw_version=coordinator.panel.firmware_version,
        )

    @property
    def is_on(self) -> bool:
        """Return if this panel is connected."""
        return self.coordinator.panel.connection_status()

    @property
    def device_class(self) -> BinarySensorDeviceClass:
        """Return the device class for this sensor."""
        return BinarySensorDeviceClass.CONNECTIVITY

    async def async_added_to_hass(self) -> None:
        """Run when entity attached to hass."""
        await super().async_added_to_hass()
        self.coordinator.panel.connection_status_observer.attach(
            self.schedule_update_ha_state
        )

    async def async_will_remove_from_hass(self) -> None:
        """Run when entity removed from hass."""
        self.coordinator.panel.connection_status_observer.detach(
            self.schedule_update_ha_state
        )
