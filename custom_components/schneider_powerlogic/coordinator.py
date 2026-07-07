"""Modbus polling coordinator for Schneider PowerLogic."""
from __future__ import annotations

import asyncio
import logging
import math
import struct
from datetime import timedelta

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

# Maximum plausible absolute value for any sensor reading.
# Anything beyond this is almost certainly a corrupted read.
_MAX_SANE_VALUE = 10_000_000.0


def _decode_float32(registers: list[int], skip_range_check: bool = False) -> float | None:
    """Decode two 16-bit Modbus registers into a float32.

    Schneider PowerLogic meters use big-endian byte order with the
    high word in the first register (standard Modbus word order).
    Returns None only for wildly out-of-range values (corrupted reads).
    NaN (Schneider N/A marker 0xFFC00000) is treated as 0.0.
    """
    raw = (registers[0] << 16) | registers[1]
    value = struct.unpack(">f", struct.pack(">I", raw))[0]

    if math.isnan(value) or math.isinf(value):
        return 0.0
    if not skip_range_check and abs(value) > _MAX_SANE_VALUE:
        return None
    return value


class ModbusCoordinator(DataUpdateCoordinator):
    """
    Polls a set of Modbus holding registers over TCP and caches the results.

    Opens a fresh TCP connection for each poll cycle to avoid transaction ID
    collisions with other Modbus clients (e.g. the built-in modbus integration)
    sharing the same meter gateway.
    """

    def __init__(
        self,
        hass: HomeAssistant,
        host: str,
        port: int,
        slave: int,
        sensors: list,
        update_interval: timedelta,
    ) -> None:
        self.host = host
        self.port = port
        self.slave = slave
        self.sensors = sensors
        self._lock = asyncio.Lock()

        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN}_{host}_{slave}_{int(update_interval.total_seconds())}s",
            update_interval=update_interval,
        )

    async def _async_update_data(self) -> dict[str, float | None]:
        """Fetch all registers for this coordinator's sensor group."""
        from pymodbus.client import AsyncModbusTcpClient  # noqa: PLC0415

        async with self._lock:
            client = AsyncModbusTcpClient(
                host=self.host,
                port=self.port,
                timeout=5,
            )
            try:
                connected = await client.connect()
                if not connected:
                    raise UpdateFailed(
                        f"Cannot connect to {self.host}:{self.port}"
                    )

                results: dict[str, float | None] = {}

                for sensor_def in self.sensors:
                    key, _label, address, data_type, *_rest = sensor_def
                    group = sensor_def[10]
                    try:
                        count = 2 if data_type == "float32" else 1
                        response = await client.read_holding_registers(
                            address=address, count=count, device_id=self.slave
                        )

                        # Check for valid register data first — some pymodbus
                        # versions report isError() True on responses that
                        # still contain usable register data.
                        if not hasattr(response, "registers") or response.registers is None:
                            _LOGGER.warning(
                                "Modbus error reading %s (address %s) from %s: %s",
                                key, address, self.host, response,
                            )
                            results[key] = None
                            continue

                        if data_type == "float32":
                            # Skip range check for energy registers (cumulative, can be very large)
                            skip_range = group == "energy"
                            value = _decode_float32(response.registers, skip_range_check=skip_range)
                            if value is None:
                                _LOGGER.debug(
                                    "Out-of-range float32 for %s (address %s): registers=%s",
                                    key, address, response.registers,
                                )
                                results[key] = None
                                continue
                        else:
                            value = float(response.registers[0])

                        results[key] = value

                    except Exception as exc:  # noqa: BLE001
                        _LOGGER.warning("Error reading %s: %s", key, exc)
                        results[key] = None

                return results

            except UpdateFailed:
                raise
            except Exception as exc:
                raise UpdateFailed(
                    f"Error polling {self.host}:{self.port}: {exc}"
                ) from exc
            finally:
                client.close()
