"""Schneider PowerLogic Modbus integration."""
from __future__ import annotations

import logging
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_PORT, Platform
from homeassistant.core import HomeAssistant

from .const import CONF_SLAVE, CONF_SENSOR_GROUPS, DOMAIN, MANDATORY_GROUPS, SENSOR_DEFINITIONS
from .coordinator import ModbusCoordinator

_LOGGER = logging.getLogger(__name__)

PLATFORMS = [Platform.SENSOR]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Schneider PowerLogic from a config entry."""
    host: str = entry.data[CONF_HOST]
    port: int = entry.data[CONF_PORT]
    slave: int = entry.data[CONF_SLAVE]

    # Filter sensor definitions to only the enabled groups
    enabled_groups: list[str] = entry.data.get(CONF_SENSOR_GROUPS, list(MANDATORY_GROUPS))
    active_sensors = [s for s in SENSOR_DEFINITIONS if s[10] in enabled_groups]

    # Build one coordinator per unique scan_interval so we batch register reads
    intervals: dict[int, list] = {}
    for sensor_def in active_sensors:
        interval = sensor_def[9]  # scan_interval
        intervals.setdefault(interval, []).append(sensor_def)

    coordinators: dict[int, ModbusCoordinator] = {}
    for interval, sensors in intervals.items():
        coordinator = ModbusCoordinator(
            hass=hass,
            host=host,
            port=port,
            slave=slave,
            sensors=sensors,
            update_interval=timedelta(seconds=interval),
        )
        await coordinator.async_config_entry_first_refresh()
        coordinators[interval] = coordinator

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinators

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok
