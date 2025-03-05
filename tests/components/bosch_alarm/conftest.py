"""Define fixtures for Bosch Alarm tests."""

import asyncio
from collections.abc import Generator
from dataclasses import dataclass
from datetime import datetime
from unittest.mock import AsyncMock, patch

from bosch_alarm_mode2.const import (
    AREA_ARMING_STATUS,
    AREA_STATUS,
    DOOR_ACTION,
    DOOR_STATUS,
    OUTPUT_STATUS,
    POINT_STATUS,
)
from bosch_alarm_mode2.panel import Area, Door, HistoryEvent, Output, Panel, Point
import pytest

from homeassistant.components.bosch_alarm.const import (
    CONF_INSTALLER_CODE,
    CONF_USER_CODE,
    DOMAIN,
)
from homeassistant.const import CONF_HOST, CONF_MODEL, CONF_PASSWORD, CONF_PORT

from tests.common import MockConfigEntry


@dataclass
class MockBoschAlarmConfig:
    """Define a class used by bosch_alarm fixtures."""

    model: str
    serial: str
    config: dict
    side_effect: Exception


@pytest.fixture
def mock_setup_entry() -> Generator[AsyncMock]:
    """Override async_setup_entry."""
    with patch(
        "homeassistant.components.bosch_alarm.async_setup_entry",
        return_value=True,
    ) as mock_setup_entry:
        yield mock_setup_entry


@pytest.fixture(name="data_solution_3000", scope="package")
def data_solution_3000_fixture() -> dict:
    """Define a testing config for configuring a Solution 3000 panel."""
    return {CONF_USER_CODE: "1234"}


@pytest.fixture(name="data_amax_3000", scope="package")
def data_amax_3000_fixture() -> dict:
    """Define a testing config for configuring an AMAX 3000 panel."""
    return {CONF_INSTALLER_CODE: "1234", CONF_PASSWORD: "1234567890"}


@pytest.fixture(name="data_b5512", scope="package")
def data_b5512_fixture() -> dict:
    """Define a testing config for configuring a B5512 panel."""
    return {CONF_PASSWORD: "1234567890"}


@pytest.fixture(name="data_areas", scope="package")
def data_areas_fixture() -> list[Area]:
    """Define a mocked area config."""
    return {1: Area("Area1", AREA_STATUS.DISARMED)}


@pytest.fixture(name="data_outputs", scope="package")
def data_outputs_fixture() -> list[Output]:
    """Define a mocked output config."""
    return {1: Output("Output A", OUTPUT_STATUS.INACTIVE)}


@pytest.fixture(name="data_doors", scope="package")
def data_doors_fixture() -> list[Door]:
    """Define a mocked door config."""
    return {1: Door("Main Door", DOOR_STATUS.LOCKED)}


@pytest.fixture(name="data_points", scope="package")
def data_points_fixture() -> list[Point]:
    """Define a mocked points config."""
    return {
        1: Point("Window", POINT_STATUS.NORMAL),
        2: Point("Door", POINT_STATUS.NORMAL),
        3: Point("Motion Detector", POINT_STATUS.NORMAL),
        4: Point("CO Detector", POINT_STATUS.NORMAL),
        5: Point("Smoke Detector", POINT_STATUS.NORMAL),
        6: Point("GlassBreak Detector", POINT_STATUS.NORMAL),
    }


@pytest.fixture(name="bosch_alarm_test_data")
def bosch_alarm_test_data_fixture(
    request: pytest.FixtureRequest,
    data_solution_3000: dict,
    data_amax_3000: dict,
    data_b5512: dict,
    data_areas: list[Area],
    data_outputs: list[Output],
    data_doors: list[Door],
    data_points: list[Point],
) -> Generator[MockBoschAlarmConfig]:
    """Define a fixture to set up Bosch Alarm."""
    if request.param == "Solution 3000":
        config = MockBoschAlarmConfig(request.param, None, data_solution_3000, None)
    if request.param == "AMAX 3000":
        config = MockBoschAlarmConfig(request.param, None, data_amax_3000, None)
    if request.param == "B5512 (US1B)":
        config = MockBoschAlarmConfig(request.param, 1234567890, data_b5512, None)

    def area_arm_update(self: Panel, area_id: int, arm_type: int) -> None:
        if arm_type == self._all_arming_id:
            self.areas[area_id].status = AREA_STATUS.ALL_ARMED[0]
            self.events.append(
                HistoryEvent(0, datetime.now(), f"Area {area_id} Armed AWAY")
            )
        if arm_type == self._partial_arming_id:
            self.areas[area_id].status = AREA_STATUS.PART_ARMED[0]
            self.events.append(
                HistoryEvent(0, datetime.now(), f"Area {area_id} Armed HOME")
            )

    async def area_arm(self: Panel, area_id: int, arm_type: int) -> None:
        if arm_type == AREA_ARMING_STATUS.DISARM:
            self.areas[area_id].status = AREA_STATUS.DISARMED
        if arm_type in (self._all_arming_id, self._partial_arming_id):
            self.areas[area_id].status = AREA_STATUS.ARMING[0]
            asyncio.get_event_loop().call_later(
                0.1, area_arm_update, self, area_id, arm_type
            )

    async def set_output_state(self: Panel, output_id: int, state: int) -> None:
        self.outputs[output_id].status = state
        self.events.append(
            HistoryEvent(0, datetime.now(), f"Output {output_id} set to {state}")
        )

    async def set_door_state(self: Panel, door_id: int, state: int) -> None:
        if state == DOOR_ACTION.UNLOCK:
            self.doors[door_id].status = DOOR_STATUS.UNLOCKED
            self.events.append(
                HistoryEvent(0, datetime.now(), f"Door {door_id} Unlocked")
            )
        if state == DOOR_ACTION.TERMINATE_UNLOCK:
            self.doors[door_id].status = DOOR_STATUS.LOCKED
            self.events.append(
                HistoryEvent(0, datetime.now(), f"Door {door_id} Locked")
            )

    async def connect(self: Panel, load_selector: int = 0):
        if config.side_effect:
            raise config.side_effect
        self.model = request.param
        self.serial_number = config.serial
        self.areas = data_areas
        self.outputs = data_outputs
        self.doors = data_doors
        self.points = data_points

    with (
        patch("bosch_alarm_mode2.panel.Panel.connect", connect),
        patch("bosch_alarm_mode2.panel.Panel._area_arm", area_arm),
        patch("bosch_alarm_mode2.panel.Panel._set_output_state", set_output_state),
        patch("bosch_alarm_mode2.panel.Panel._door_set_state", set_door_state),
    ):
        yield config


@pytest.fixture(name="bosch_config_entry")
def bosch_config_entry_fixture(
    bosch_alarm_test_data: MockBoschAlarmConfig,
) -> Generator[MockConfigEntry]:
    """Mock config entry for bosch alarm."""
    return MockConfigEntry(
        domain=DOMAIN,
        unique_id="unique_id",
        entry_id=bosch_alarm_test_data.model,
        data={
            CONF_HOST: "0.0.0.0",
            CONF_PORT: 7700,
            CONF_MODEL: bosch_alarm_test_data.model,
            **bosch_alarm_test_data.config,
        },
    )
