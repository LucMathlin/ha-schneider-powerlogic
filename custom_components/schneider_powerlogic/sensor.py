"""Sensor platform for Schneider PowerLogic Modbus integration."""
from __future__ import annotations

import logging

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_PORT
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import CONF_SLAVE, CONF_NAME, CONF_INVERT_POWER, CONF_SENSOR_GROUPS, DOMAIN, INVERTIBLE_KEYS, MANDATORY_GROUPS, SENSOR_DEFINITIONS
from .coordinator import ModbusCoordinator

_LOGGER = logging.getLogger(__name__)

# Map string names from const.py to HA SensorDeviceClass enum values
DEVICE_CLASS_MAP: dict[str, SensorDeviceClass | None] = {
    "voltage":      SensorDeviceClass.VOLTAGE,
    "current":      SensorDeviceClass.CURRENT,
    "power":        SensorDeviceClass.POWER,
    "energy":       SensorDeviceClass.ENERGY,
    "frequency":    SensorDeviceClass.FREQUENCY,
    "temperature":  SensorDeviceClass.TEMPERATURE,
    "power_factor": SensorDeviceClass.POWER_FACTOR,
    None:           None,
}

STATE_CLASS_MAP: dict[str, SensorStateClass | None] = {
    "measurement":       SensorStateClass.MEASUREMENT,
    "total_increasing":  SensorStateClass.TOTAL_INCREASING,
    "total":             SensorStateClass.TOTAL,
    None:                None,
}


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up PowerLogic sensors from a config entry."""
    coordinators: dict[int, ModbusCoordinator] = hass.data[DOMAIN][entry.entry_id]
    meter_name: str = entry.data[CONF_NAME]
    host: str = entry.data[CONF_HOST]
    port: int = entry.data[CONF_PORT]
    slave: int = entry.data[CONF_SLAVE]

    enabled_groups: list[str] = entry.data.get(CONF_SENSOR_GROUPS, list(MANDATORY_GROUPS))
    active_sensors = [s for s in SENSOR_DEFINITIONS if s[10] in enabled_groups]
    invert_power: bool = entry.data.get(CONF_INVERT_POWER, False)

    entities: list[PowerLogicSensor] = []

    for sensor_def in active_sensors:
        (
            key,
            label_suffix,
            address,
            data_type,
            unit,
            device_class_str,
            state_class_str,
            scale,
            precision,
            scan_interval,
            _group,
        ) = sensor_def

        coordinator = coordinators[scan_interval]

        entities.append(
            PowerLogicSensor(
                coordinator=coordinator,
                entry_id=entry.entry_id,
                meter_name=meter_name,
                host=host,
                port=port,
                slave=slave,
                key=key,
                label_suffix=label_suffix,
                unit=unit,
                device_class_str=device_class_str,
                state_class_str=state_class_str,
                scale=scale,
                precision=precision,
                invert=invert_power and key in INVERTIBLE_KEYS,
            )
        )

    async_add_entities(entities)


class PowerLogicSensor(CoordinatorEntity, SensorEntity):
    """Represents a single register from a PowerLogic meter."""

    def __init__(
        self,
        coordinator: ModbusCoordinator,
        entry_id: str,
        meter_name: str,
        host: str,
        port: int,
        slave: int,
        key: str,
        label_suffix: str,
        unit: str | None,
        device_class_str: str | None,
        state_class_str: str | None,
        scale: float | None,
        precision: int | None,
        invert: bool = False,
    ) -> None:
        super().__init__(coordinator)

        self._key = key
        self._meter_name = meter_name
        self._scale = scale
        self._precision = precision
        self._invert = invert

        # Entity name: "DB-1 Voltage L1-N"
        self._attr_name = f"{meter_name} {label_suffix}"

        # Unique ID scoped to this HA instance + meter + register
        self._attr_unique_id = f"{entry_id}_{key}"

        self._attr_native_unit_of_measurement = unit
        self._attr_device_class = DEVICE_CLASS_MAP.get(device_class_str)
        self._attr_state_class = STATE_CLASS_MAP.get(state_class_str)
        self._attr_suggested_display_precision = precision

        # Group all sensors from this meter under one device card
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, f"{host}_{port}_{slave}")},
            name=meter_name,
            manufacturer="Schneider Electric",
            model="PowerLogic (Modbus TCP)",
            configuration_url=f"http://{host}",
        )

    @property
    def native_value(self) -> float | None:
        """Return the current sensor value, applying scale, inversion, and precision."""
        raw: float | None = self.coordinator.data.get(self._key)
        if raw is None:
            return None

        value = raw * self._scale if self._scale is not None else raw

        if self._invert:
            value = -value

        if self._precision is not None:
            value = round(value, self._precision)

        return value

    @property
    def available(self) -> bool:
        """Mark unavailable if the coordinator failed or returned None for this key."""
        return (
            self.coordinator.last_update_success
            and self.coordinator.data is not None
            and self.coordinator.data.get(self._key) is not None
        )
