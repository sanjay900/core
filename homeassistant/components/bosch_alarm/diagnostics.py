"""Diagnostics for bosch alarm."""

from typing import Any

from homeassistant.components.diagnostics import async_redact_data
from homeassistant.const import CONF_PASSWORD
from homeassistant.core import HomeAssistant

from .const import CONF_INSTALLER_CODE, CONF_USER_CODE
from .coordinator import BoschAlarmConfigEntry

TO_REDACT = [CONF_INSTALLER_CODE, CONF_USER_CODE, CONF_PASSWORD]


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant, entry: BoschAlarmConfigEntry
) -> dict[str, Any]:
    """Return diagnostics for a config entry."""

    return {
        "entry_data": async_redact_data(entry.data, TO_REDACT),
        "data": entry.runtime_data.data,
    }
