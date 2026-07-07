# Schneider PowerLogic Modbus

[![Validate](https://github.com/LucMathlin/ha-schneider-powerlogic/actions/workflows/validate.yml/badge.svg)](https://github.com/LucMathlin/ha-schneider-powerlogic/actions/workflows/validate.yml)
[![HACS Custom](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)

[![Add to HACS](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=LucMathlin&repository=ha-schneider-powerlogic&category=integration)

A Home Assistant custom integration for Schneider Electric PowerLogic power meters via Modbus TCP.

## Supported Devices

- Schneider PowerLogic PM5xxx series (PM5100, PM5300, PM5500, etc.)
- Other PowerLogic meters supporting Modbus TCP

## Features

- Real-time power monitoring (voltage, current, power, energy)
- Power quality metrics (power factor, THD, frequency)
- Per-phase and total readings
- Configurable via the Home Assistant UI (config flow)

## Installation

### HACS (Recommended)

1. Open HACS in Home Assistant
2. Click the three dots menu → **Custom repositories**
3. Add `https://github.com/LucMathlin/ha-schneider-powerlogic` with category **Integration**
4. Search for "Schneider PowerLogic" and install
5. Restart Home Assistant

### Manual

1. Copy `custom_components/schneider_powerlogic/` to your Home Assistant `config/custom_components/` directory
2. Restart Home Assistant

## Configuration

1. Go to **Settings → Devices & Services → Add Integration**
2. Search for "Schneider PowerLogic"
3. Enter the Modbus TCP host, port, and slave ID
4. Configure polling interval as needed

## Requirements

- Modbus TCP connectivity to the power meter
- `pymodbus>=3.11.2` (installed automatically)
