"""Config flow for Schneider PowerLogic Modbus integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_PORT
from homeassistant.core import HomeAssistant
from homeassistant.helpers.selector import (
    BooleanSelector,
    NumberSelector,
    NumberSelectorConfig,
    NumberSelectorMode,
    TextSelector,
)

from .const import (
    CONF_INVERT_POWER,
    CONF_NAME,
    CONF_SENSOR_GROUPS,
    CONF_SLAVE,
    DEFAULT_PORT,
    DEFAULT_SLAVE,
    DOMAIN,
    MANDATORY_GROUPS,
    SENSOR_GROUPS,
)

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_NAME): TextSelector(),
        vol.Required(CONF_HOST): TextSelector(),
        vol.Optional(CONF_PORT, default=DEFAULT_PORT): NumberSelector(
            NumberSelectorConfig(min=1, max=65535, step=1, mode=NumberSelectorMode.BOX)
        ),
        vol.Optional(CONF_SLAVE, default=DEFAULT_SLAVE): NumberSelector(
            NumberSelectorConfig(min=0, max=255, step=1, mode=NumberSelectorMode.BOX)
        ),
    }
)


def _build_groups_schema() -> vol.Schema:
    """Build the sensor groups selection schema — mandatory groups pre-ticked and hidden."""
    fields: dict = {}
    for group_key, _label in SENSOR_GROUPS.items():
        if group_key not in MANDATORY_GROUPS:
            fields[vol.Optional(group_key, default=True)] = BooleanSelector()
    # Power inversion option
    fields[vol.Optional(CONF_INVERT_POWER, default=False)] = BooleanSelector()
    return vol.Schema(fields)


async def _test_connection(hass: HomeAssistant, host: str, port: int, slave: int) -> str | None:
    """Try to connect and read a single register. Returns None on success or an error key."""
    try:
        from pymodbus.client import AsyncModbusTcpClient  # noqa: PLC0415

        client = AsyncModbusTcpClient(host=host, port=port, timeout=5)
        connected = await client.connect()
        if not connected:
            return "cannot_connect"

        result = await client.read_holding_registers(address=3027, count=2, device_id=slave)
        client.close()

        if result.isError():
            return "invalid_slave"

        return None

    except ConnectionRefusedError:
        return "cannot_connect"
    except Exception as exc:  # noqa: BLE001
        _LOGGER.exception(
            "Unexpected error testing connection to %s:%s slave %s: %s",
            host, port, slave, exc,
        )
        return "unknown"


class SchneiderPowerLogicConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle the config flow for Schneider PowerLogic."""

    VERSION = 1

    def __init__(self) -> None:
        """Initialise the flow."""
        self._connection_data: dict[str, Any] = {}

    async def async_step_user(self, user_input: dict[str, Any] | None = None):
        """Step 1 — connection details."""
        errors: dict[str, str] = {}

        if user_input is not None:
            host: str = user_input[CONF_HOST].strip()
            port: int = int(user_input[CONF_PORT])
            slave: int = int(user_input[CONF_SLAVE])
            name: str = user_input[CONF_NAME].strip()

            await self.async_set_unique_id(f"{host}_{port}_{slave}")
            self._abort_if_unique_id_configured()

            error = await _test_connection(self.hass, host, port, slave)
            if error:
                errors["base"] = error
            else:
                # Store connection data and move to sensor group selection
                self._connection_data = {
                    CONF_NAME: name,
                    CONF_HOST: host,
                    CONF_PORT: port,
                    CONF_SLAVE: slave,
                }
                return await self.async_step_sensors()

        return self.async_show_form(
            step_id="user",
            data_schema=STEP_USER_DATA_SCHEMA,
            errors=errors,
        )

    async def async_step_sensors(self, user_input: dict[str, Any] | None = None):
        """Step 2 — choose which sensor groups to enable."""
        if user_input is not None:
            # Always include mandatory groups
            enabled_groups = list(MANDATORY_GROUPS)
            for group_key in SENSOR_GROUPS:
                if group_key not in MANDATORY_GROUPS and user_input.get(group_key, True):
                    enabled_groups.append(group_key)

            return self.async_create_entry(
                title=self._connection_data[CONF_NAME],
                data={
                    **self._connection_data,
                    CONF_SENSOR_GROUPS: enabled_groups,
                    CONF_INVERT_POWER: user_input.get(CONF_INVERT_POWER, False),
                },
            )

        return self.async_show_form(
            step_id="sensors",
            data_schema=_build_groups_schema(),
            description_placeholders={
                "note": "Active Power sensors are always included."
            },
        )
