"""Tests for the bosch_alarm config flow."""

import asyncio
from typing import Any
from unittest.mock import AsyncMock

import pytest

from homeassistant import config_entries
from homeassistant.components.bosch_alarm.const import DOMAIN
from homeassistant.config_entries import SOURCE_USER
<<<<<<< Updated upstream
from homeassistant.const import CONF_HOST, CONF_MODEL, CONF_PORT
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType
=======
from homeassistant.const import CONF_CODE, CONF_HOST, CONF_MODEL, CONF_PORT
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType
from homeassistant.helpers.service_info.dhcp import DhcpServiceInfo
>>>>>>> Stashed changes

from tests.common import MockConfigEntry


async def test_form_user(
    hass: HomeAssistant,
    mock_setup_entry: AsyncMock,
    mock_panel: AsyncMock,
    model_name: str,
    serial_number: str,
    config_flow_data: dict[str, Any],
) -> None:
    """Test the config flow for bosch_alarm."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": SOURCE_USER}
    )
    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "user"
    assert result["errors"] == {}
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {CONF_HOST: "1.1.1.1", CONF_PORT: 7700},
    )
    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "auth"
    assert result["errors"] == {}
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        config_flow_data,
    )
    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["title"] == f"Bosch {model_name}"
    assert (
        result["data"]
        == {
            CONF_HOST: "1.1.1.1",
            CONF_PORT: 7700,
            CONF_MODEL: model_name,
        }
        | config_flow_data
    )
    assert result["result"].unique_id == serial_number
    assert len(mock_setup_entry.mock_calls) == 1


@pytest.mark.parametrize(
    ("exception", "message"),
    [
        (asyncio.TimeoutError, "cannot_connect"),
        (Exception, "unknown"),
    ],
)
async def test_form_exceptions(
    hass: HomeAssistant,
    mock_setup_entry: AsyncMock,
    mock_panel: AsyncMock,
    config_flow_data: dict[str, Any],
    exception: Exception,
    message: str,
) -> None:
    """Test we handle exceptions correctly."""

    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "user"
    assert result["errors"] == {}
    mock_panel.connect.side_effect = exception
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {CONF_HOST: "1.1.1.1", CONF_PORT: 7700},
    )
    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "user"
    assert result["errors"] == {"base": message}

    mock_panel.connect.side_effect = None
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {CONF_HOST: "1.1.1.1", CONF_PORT: 7700},
    )
    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "auth"
    assert result["errors"] == {}

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        config_flow_data,
    )
    assert result["type"] is FlowResultType.CREATE_ENTRY


@pytest.mark.parametrize(
    ("exception", "message"),
    [
        (PermissionError, "invalid_auth"),
        (asyncio.TimeoutError, "cannot_connect"),
        (Exception, "unknown"),
    ],
)
async def test_form_exceptions_user(
    hass: HomeAssistant,
    mock_setup_entry: AsyncMock,
    mock_panel: AsyncMock,
    config_flow_data: dict[str, Any],
    exception: Exception,
    message: str,
) -> None:
    """Test we handle exceptions correctly."""

    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": SOURCE_USER}
    )
    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "user"
    assert result["errors"] == {}

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {CONF_HOST: "1.1.1.1", CONF_PORT: 7700},
    )
    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "auth"
    assert result["errors"] == {}
    mock_panel.connect.side_effect = exception

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], config_flow_data
    )
    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "auth"
    assert result["errors"] == {"base": message}

    mock_panel.connect.side_effect = None

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], config_flow_data
    )
    assert result["type"] is FlowResultType.CREATE_ENTRY


@pytest.mark.parametrize("model", ["solution_3000", "amax_3000"])
async def test_entry_already_configured_host(
    hass: HomeAssistant,
    mock_config_entry: MockConfigEntry,
    mock_panel: AsyncMock,
    config_flow_data: dict[str, Any],
) -> None:
    """Test if configuring an entity twice results in an error."""
    mock_config_entry.add_to_hass(hass)

    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": SOURCE_USER}
    )

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {CONF_HOST: "0.0.0.0"}
    )

    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "auth"
    assert result["errors"] == {}
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], config_flow_data
    )

    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "already_configured"


@pytest.mark.parametrize("model", ["b5512"])
async def test_entry_already_configured_serial(
    hass: HomeAssistant,
    mock_config_entry: MockConfigEntry,
    mock_panel: AsyncMock,
    config_flow_data: dict[str, Any],
) -> None:
    """Test if configuring an entity twice results in an error."""
    mock_config_entry.add_to_hass(hass)

    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": SOURCE_USER}
    )

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {CONF_HOST: "0.0.0.0"}
    )

    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "auth"
    assert result["errors"] == {}
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], config_flow_data
    )

    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "already_configured"
<<<<<<< Updated upstream
=======

    await hass.async_block_till_done()
    assert len(mock_setup_entry.mock_calls) == 0


@pytest.mark.parametrize(
    "bosch_alarm_test_data",
    [
        "Solution 3000",
        "AMAX 3000",
        "B5512 (US1B)",
    ],
    indirect=True,
)
@pytest.mark.usefixtures("bosch_alarm_test_data")
async def test_options_flow(
    hass: HomeAssistant,
    mock_setup_entry: AsyncMock,
    bosch_alarm_test_data: MockBoschAlarmConfig,
) -> None:
    """Test the options flow for bosch_alarm."""
    config_entry = MockConfigEntry(
        domain=DOMAIN,
        data={
            CONF_HOST: "1.1.1.1",
            CONF_PORT: 7700,
            CONF_MODEL: bosch_alarm_test_data.model,
            **bosch_alarm_test_data.config,
        },
        version=1,
        minor_version=2,
    )
    config_entry.add_to_hass(hass)

    assert await hass.config_entries.async_setup(config_entry.entry_id)

    result = await hass.config_entries.options.async_init(config_entry.entry_id)
    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "init"

    result = await hass.config_entries.options.async_configure(
        result["flow_id"],
        user_input={CONF_CODE: "1234"},
    )

    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["result"] is True

    assert config_entry.options == {CONF_CODE: "1234"}

    await hass.async_block_till_done()
    assert len(mock_setup_entry.mock_calls) == 1


@pytest.mark.parametrize(
    ("bosch_alarm_test_data", "bosch_config_entry"),
    [
        ("Solution 3000", None),
        ("AMAX 3000", None),
        ("B5512 (US1B)", None),
    ],
    indirect=True,
)
async def test_reauth_flow(
    hass: HomeAssistant,
    bosch_alarm_test_data: MockBoschAlarmConfig,
    bosch_config_entry: MockConfigEntry,
) -> None:
    """Test reauth flow."""
    bosch_alarm_test_data.side_effect = PermissionError()
    bosch_config_entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(bosch_config_entry.entry_id) is False
    await hass.async_block_till_done()
    result = next(
        bosch_config_entry.async_get_active_flows(hass, {config_entries.SOURCE_REAUTH})
    )

    bosch_alarm_test_data.config = {
        k: f"{v}2" for k, v in bosch_alarm_test_data.config.items()
    }

    assert result["step_id"] == "reauth_confirm"
    # Check if reauth fails if the alarm returns a permission error
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        user_input=bosch_alarm_test_data.config,
    )
    assert result["step_id"] == "reauth_confirm"
    assert result["errors"]["base"] == "invalid_auth"
    # Check if reauth fails if the alarm returns a connection error
    bosch_alarm_test_data.side_effect = OSError()
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        user_input=bosch_alarm_test_data.config,
    )
    assert result["step_id"] == "reauth_confirm"
    assert result["errors"]["base"] == "cannot_connect"
    # Check if reauth fails if the alarm returns a unknown error
    bosch_alarm_test_data.side_effect = Exception()
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        user_input=bosch_alarm_test_data.config,
    )
    assert result["step_id"] == "reauth_confirm"
    assert result["errors"]["base"] == "unknown"
    # Now check it works when there are no errors
    bosch_alarm_test_data.side_effect = None
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        user_input=bosch_alarm_test_data.config,
    )
    assert result["reason"] == "reauth_successful"
    compare = {**bosch_config_entry.data, **bosch_alarm_test_data.config}
    assert compare == bosch_config_entry.data


@pytest.mark.parametrize(
    ("bosch_alarm_test_data", "bosch_config_entry"),
    [
        ("Solution 3000", None),
        ("AMAX 3000", None),
        ("B5512 (US1B)", None),
    ],
    indirect=True,
)
async def test_reconfig_flow(
    hass: HomeAssistant,
    bosch_alarm_test_data: MockBoschAlarmConfig,
    bosch_config_entry: MockConfigEntry,
) -> None:
    """Test reconfig auth."""
    bosch_config_entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(bosch_config_entry.entry_id)
    await hass.async_block_till_done()

    bosch_alarm_test_data.config = {
        k: f"{v}2" for k, v in bosch_alarm_test_data.config.items()
    }
    result = await hass.config_entries.flow.async_init(
        DOMAIN,
        context={
            "source": config_entries.SOURCE_RECONFIGURE,
            "entry_id": bosch_config_entry.entry_id,
        },
    )

    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "user"
    assert result["errors"] == {}
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {CONF_HOST: "1.1.1.1", CONF_PORT: 7700},
    )
    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "auth"
    assert result["errors"] == {}
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        bosch_alarm_test_data.config,
    )
    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "reconfigure_successful"
    assert bosch_config_entry.data == {
        CONF_HOST: "1.1.1.1",
        CONF_PORT: 7700,
        CONF_MODEL: bosch_alarm_test_data.model,
        **bosch_alarm_test_data.config,
    }

    await hass.async_block_till_done()


@pytest.mark.parametrize(
    ("bosch_alarm_test_data", "bosch_config_entry", "other_panel"),
    [
        ("Solution 3000", None, "Solution 2000"),
        ("AMAX 3000", None, "AMAX 2000"),
        ("B5512 (US1B)", None, "B5512 (US1A)"),
    ],
    indirect=("bosch_alarm_test_data", "bosch_config_entry"),
)
async def test_reconfig_flow_incorrect_model(
    hass: HomeAssistant,
    bosch_alarm_test_data: MockBoschAlarmConfig,
    bosch_config_entry: MockConfigEntry,
    other_panel: str,
) -> None:
    """Test reconfig fails with a different device."""
    bosch_config_entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(bosch_config_entry.entry_id)
    await hass.async_block_till_done()

    bosch_alarm_test_data.config = {
        k: f"{v}2" for k, v in bosch_alarm_test_data.config.items()
    }
    result = await hass.config_entries.flow.async_init(
        DOMAIN,
        context={
            "source": config_entries.SOURCE_RECONFIGURE,
            "entry_id": bosch_config_entry.entry_id,
        },
    )

    bosch_alarm_test_data.model = other_panel

    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "user"
    assert result["errors"] == {}
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {CONF_HOST: "0.0.0.0", CONF_PORT: 7700},
    )

    await hass.async_block_till_done()
    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "auth"
    assert result["errors"] == {}
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        bosch_alarm_test_data.config,
    )

    await hass.async_block_till_done()
    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "unique_id_mismatch"


@pytest.mark.usefixtures("bosch_alarm_test_data")
@pytest.mark.parametrize(
    ("bosch_alarm_test_data"),
    [
        ("Solution 3000"),
        ("AMAX 3000"),
        ("B5512 (US1B)"),
    ],
    indirect=["bosch_alarm_test_data"],
)
async def test_dhcp_can_finish(
    hass: HomeAssistant,
    bosch_alarm_test_data: MockBoschAlarmConfig,
) -> None:
    """Test DHCP discovery flow can finish right away."""

    result = await hass.config_entries.flow.async_init(
        DOMAIN,
        context={"source": config_entries.SOURCE_DHCP},
        data=DhcpServiceInfo(
            hostname="test",
            ip="1.1.1.1",
            macaddress="34ea34b43b5a",
        ),
    )
    await hass.async_block_till_done()
    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "auth"
    assert result["errors"] == {}
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        bosch_alarm_test_data.config,
    )

    await hass.async_block_till_done()

    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["title"] == f"Bosch {bosch_alarm_test_data.model}"
    assert result["data"] == {
        CONF_HOST: "1.1.1.1",
        CONF_PORT: 7700,
        CONF_MODEL: bosch_alarm_test_data.model,
        **bosch_alarm_test_data.config,
    }


@pytest.mark.usefixtures("bosch_alarm_test_data")
@pytest.mark.parametrize(
    ("bosch_alarm_test_data", "exception", "message"),
    [
        ("Solution 3000", asyncio.exceptions.TimeoutError(), "cannot_connect"),
        ("Solution 3000", Exception(), "unknown"),
        ("AMAX 3000", asyncio.exceptions.TimeoutError(), "cannot_connect"),
        ("AMAX 3000", Exception(), "unknown"),
        ("B5512 (US1B)", asyncio.exceptions.TimeoutError(), "cannot_connect"),
        ("B5512 (US1B)", Exception(), "unknown"),
    ],
    indirect=["bosch_alarm_test_data"],
)
async def test_dhcp_exceptions(
    hass: HomeAssistant,
    mock_setup_entry: AsyncMock,
    bosch_alarm_test_data: MockBoschAlarmConfig,
    exception: Exception,
    message: str,
) -> None:
    """Test DHCP discovery flow that fails to connect."""
    bosch_alarm_test_data.side_effect = exception
    result = await hass.config_entries.flow.async_init(
        DOMAIN,
        context={"source": config_entries.SOURCE_DHCP},
        data=DhcpServiceInfo(
            hostname="test",
            ip="1.1.1.1",
            macaddress="34ea34b43b5a",
        ),
    )
    await hass.async_block_till_done()
    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == message


@pytest.mark.parametrize(
    ("bosch_alarm_test_data", "bosch_config_entry"),
    [
        ("Solution 3000", None),
        ("AMAX 3000", None),
        ("B5512 (US1B)", None),
    ],
    indirect=True,
)
async def test_dhcp_already_exists(
    hass: HomeAssistant,
    mock_setup_entry: AsyncMock,
    bosch_config_entry: MockConfigEntry,
    bosch_alarm_test_data: MockBoschAlarmConfig,
) -> None:
    """Test DHCP discovery flow that fails to connect."""

    bosch_config_entry.add_to_hass(hass)

    assert await hass.config_entries.async_setup(bosch_config_entry.entry_id)

    result = await hass.config_entries.flow.async_init(
        DOMAIN,
        context={"source": config_entries.SOURCE_DHCP},
        data=DhcpServiceInfo(
            hostname="test",
            ip="0.0.0.0",
            macaddress="34ea34b43b5a",
        ),
    )
    await hass.async_block_till_done()

    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "already_configured"


@pytest.mark.usefixtures("bosch_alarm_test_data")
@pytest.mark.parametrize(
    ("bosch_alarm_test_data"),
    [
        ("Solution 3000"),
        ("AMAX 3000"),
        ("B5512 (US1B)"),
    ],
    indirect=["bosch_alarm_test_data"],
)
async def test_dhcp_updates_host(
    hass: HomeAssistant,
    mock_setup_entry: AsyncMock,
    bosch_alarm_test_data: MockBoschAlarmConfig,
) -> None:
    """Test DHCP updates host."""

    config_entry = MockConfigEntry(
        domain=DOMAIN,
        data={
            CONF_HOST: "1.1.1.1",
            CONF_PORT: 7700,
            CONF_MODEL: bosch_alarm_test_data.model,
            **bosch_alarm_test_data.config,
        },
        unique_id="34:ea:34:b4:3b:5a",
        version=1,
        minor_version=2,
    )
    config_entry.add_to_hass(hass)

    assert await hass.config_entries.async_setup(config_entry.entry_id)

    result = await hass.config_entries.flow.async_init(
        DOMAIN,
        context={"source": config_entries.SOURCE_DHCP},
        data=DhcpServiceInfo(
            hostname="test",
            ip="4.5.6.7",
            macaddress="34ea34b43b5a",
        ),
    )
    await hass.async_block_till_done()

    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "already_configured"
    assert config_entry.data["host"] == "4.5.6.7"
>>>>>>> Stashed changes
