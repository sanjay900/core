"""Support for Bosch Alarm Panel History as a sensor."""

from __future__ import annotations

from homeassistant.components.sensor import SensorEntity
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import BoschAlarmConfigEntry, BoschAlarmCoordinator

READY_STATE_NO = "no"
READY_STATE_HOME = "home"
READY_STATE_AWAY = "away"


async def async_setup_entry(
    hass: HomeAssistant | None,
    config_entry: BoschAlarmConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up a sensor for tracking panel history."""

    coordinator: BoschAlarmCoordinator = config_entry.runtime_data
    async_add_entities(
        [
            PanelHistorySensor(coordinator),
            PanelFaultsSensor(coordinator),
        ]
    )
    async_add_entities(
        AreaReadyToArmSensor(
            coordinator,
            area_id,
        )
        for area_id in coordinator.panel.areas
    )
    async_add_entities(
        FaultingPointsSensor(
            coordinator,
            area_id,
        )
        for area_id in coordinator.panel.areas
    )
    async_add_entities(
        AreaAlarmsSensor(
            coordinator,
            area_id,
        )
        for area_id in coordinator.panel.areas
    )


class PanelHistorySensor(CoordinatorEntity[BoschAlarmCoordinator], SensorEntity):
    """A history sensor entity for a bosch alarm panel."""

    _attr_has_entity_name = True
    _attr_name = "History"

    def __init__(self, coordinator: BoschAlarmCoordinator) -> None:
        """Set up a history sensor entity for a bosch alarm panel."""
        super().__init__(coordinator)
        self._attr_entity_category = EntityCategory.DIAGNOSTIC
        self._attr_unique_id = f"{coordinator.config_entry.entry_id}_history"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, coordinator.config_entry.entry_id)},
            name=f"Bosch {coordinator.panel.model}",
            manufacturer="Bosch Security Systems",
            model=coordinator.panel.model,
            sw_version=coordinator.panel.firmware_version,
        )

    @property
    def icon(self) -> str | None:
        """The icon for this history entity."""
        return "mdi:history"

    @property
    def native_value(self) -> str:
        """The state for this history entity."""
        events = self.coordinator.panel.events
        if events:
            return str(events[-1])
        return "No events"

    async def async_added_to_hass(self) -> None:
        """Observe state changes."""
        await super().async_added_to_hass()
        self.coordinator.panel.history_observer.attach(self.schedule_update_ha_state)

    async def async_will_remove_from_hass(self) -> None:
        """Stop observing state changes."""
        self.coordinator.panel.history_observer.detach(self.schedule_update_ha_state)


class PanelFaultsSensor(CoordinatorEntity[BoschAlarmCoordinator], SensorEntity):
    """A faults sensor entity for a bosch alarm panel."""

    _attr_has_entity_name = True
    _attr_name = "Faults"

    def __init__(self, coordinator: BoschAlarmCoordinator) -> None:
        """Set up a faults sensor entity for a bosch alarm panel."""
        super().__init__(coordinator)
        self._attr_entity_category = EntityCategory.DIAGNOSTIC
        self._attr_unique_id = f"{coordinator.config_entry.entry_id}_faults"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, coordinator.config_entry.entry_id)},
            name=f"Bosch {coordinator.panel.model}",
            manufacturer="Bosch Security Systems",
            model=coordinator.panel.model,
            sw_version=coordinator.panel.firmware_version,
        )

    @property
    def icon(self) -> str:
        """The icon for this faults entity."""
        return "mdi:alert-circle-outline"

    @property
    def native_value(self) -> str:
        """The state of this faults entity."""
        faults = self.coordinator.panel.panel_faults
        return "\n".join(faults) if faults else "No faults"

    async def async_added_to_hass(self) -> None:
        """Observe state changes."""
        await super().async_added_to_hass()
        self.coordinator.panel.faults_observer.attach(self.schedule_update_ha_state)

    async def async_will_remove_from_hass(self) -> None:
        """Stop observing state changes."""
        self.coordinator.panel.faults_observer.detach(self.schedule_update_ha_state)


class FaultingPointsSensor(CoordinatorEntity[BoschAlarmCoordinator], SensorEntity):
    """A faults sensor entity for a bosch alarm panel."""

    _attr_has_entity_name = True
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    def __init__(self, coordinator: BoschAlarmCoordinator, area_id: int) -> None:
        """Set up a faults sensor entity for a bosch alarm panel."""
        super().__init__(coordinator)
        self._area = coordinator.panel.areas[area_id]
        self._attr_unique_id = f"{coordinator.config_entry.entry_id}_{area_id}_faults"
        self._attr_name = f"{self._area.name} Faulting Points"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, coordinator.config_entry.entry_id)},
            name=f"Bosch {coordinator.panel.model}",
            manufacturer="Bosch Security Systems",
            model=coordinator.panel.model,
            sw_version=coordinator.panel.firmware_version,
        )

    @property
    def icon(self) -> str:
        """The icon for this faults entity."""
        return "mdi:alert-circle-outline"

    @property
    def native_value(self) -> str:
        """The state of this faults entity."""
        return f"{self._area.faults}"

    async def async_added_to_hass(self) -> None:
        """Observe state changes."""
        await super().async_added_to_hass()
        self.coordinator.panel.faults_observer.attach(self.schedule_update_ha_state)

    async def async_will_remove_from_hass(self) -> None:
        """Stop observing state changes."""
        self.coordinator.panel.faults_observer.detach(self.schedule_update_ha_state)


class AreaReadyToArmSensor(CoordinatorEntity[BoschAlarmCoordinator], SensorEntity):
    """A sensor entity showing the ready state for an area for a bosch alarm panel."""

    _attr_has_entity_name = True

    def __init__(self, coordinator: BoschAlarmCoordinator, area_id: int) -> None:
        """Set up a faults sensor entity for a bosch alarm panel."""
        super().__init__(coordinator)
        self._attr_entity_category = EntityCategory.DIAGNOSTIC
        self._area = coordinator.panel.areas[area_id]
        self._attr_unique_id = (
            f"{coordinator.config_entry.entry_id}_{area_id}_ready_to_arm"
        )
        self._attr_should_poll = False
        self._attr_name = f"{self._area.name} Ready To Arm"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, coordinator.config_entry.entry_id)},
            name=f"Bosch {coordinator.panel.model}",
            manufacturer="Bosch Security Systems",
            model=coordinator.panel.model,
            sw_version=coordinator.panel.firmware_version,
        )

    @property
    def icon(self) -> str:
        """The icon for this entity."""
        return "mdi:information-outline"

    @property
    def native_value(self) -> str:
        """The state of this entity."""
        if self._area.all_ready:
            return READY_STATE_AWAY
        if self._area.part_ready:
            return READY_STATE_HOME
        return READY_STATE_NO

    async def async_added_to_hass(self) -> None:
        """Observe state changes."""
        await super().async_added_to_hass()
        self._area.ready_observer.attach(self.schedule_update_ha_state)

    async def async_will_remove_from_hass(self) -> None:
        """Stop observing state changes."""
        self._area.ready_observer.attach(self.schedule_update_ha_state)


class AreaAlarmsSensor(CoordinatorEntity[BoschAlarmCoordinator], SensorEntity):
    """A sensor entity showing the alarms for an area for a bosch alarm panel."""

    _attr_has_entity_name = True

    def __init__(self, coordinator: BoschAlarmCoordinator, area_id: int) -> None:
        """Set up a faults sensor entity for a bosch alarm panel."""
        super().__init__(coordinator)
        self._attr_entity_category = EntityCategory.DIAGNOSTIC
        self._area = coordinator.panel.areas[area_id]
        self._attr_unique_id = f"{coordinator.config_entry.entry_id}_{area_id}_alarms"
        self._attr_should_poll = False
        self._attr_name = f"{self._area.name} Alarms"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, coordinator.config_entry.entry_id)},
            name=f"Bosch {coordinator.panel.model}",
            manufacturer="Bosch Security Systems",
            model=coordinator.panel.model,
            sw_version=coordinator.panel.firmware_version,
        )

    @property
    def icon(self) -> str:
        """The icon for this alarms entity."""
        return "mdi:alert-circle-outline"

    @property
    def native_value(self) -> str:
        """The state of this alarms entity."""
        return "\n".join(self._area.alarms) if self._area.alarms else "No Alarms"

    async def async_added_to_hass(self) -> None:
        """Observe state changes."""
        await super().async_added_to_hass()
        self._area.alarm_observer.attach(self.schedule_update_ha_state)

    async def async_will_remove_from_hass(self) -> None:
        """Stop observing state changes."""
        self._area.alarm_observer.attach(self.schedule_update_ha_state)
