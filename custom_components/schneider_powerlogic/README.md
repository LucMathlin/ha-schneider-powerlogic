# Schneider PowerLogic Modbus — Home Assistant Custom Integration

Adds Schneider PowerLogic meters (PM5000, PM8000, etc.) via Modbus TCP with a
UI-based setup flow. No more editing `configuration.yaml`.

## What it creates

For each meter you add, **27 sensors** are automatically created and grouped
under a single device card:

| Group | Sensors |
|---|---|
| Voltages | L1-N, L2-N, L3-N, L1-L2, L2-L3, L3-L1, L-L Avg, L-N Avg |
| Currents | L1, L2, L3, N, Avg |
| Active Power | L1, L2, L3, Total |
| Other Power | Apparent, Reactive, Power Factor |
| Misc | Frequency, Temperature |
| Energy | Active Delivered (kWh), Active Received (kWh) |
| THD | Voltage L-L, Current L1/L2/L3/N |

## Installation

### HACS (recommended)
1. Add this repo as a custom repository in HACS (type: Integration).
2. Install **Schneider PowerLogic Modbus**.
3. Restart Home Assistant.

### Manual
1. Copy the `schneider_powerlogic` folder into your
   `config/custom_components/` directory.
2. Restart Home Assistant.

## Setup

1. Go to **Settings → Devices & Services → Add Integration**.
2. Search for **Schneider PowerLogic Modbus**.
3. Fill in the form:

   | Field | Example | Notes |
   |---|---|---|
   | Meter Name | `DB-1` | Used as a prefix for all sensor names |
   | IP Address | `10.20.0.41` | Meter's IP on your network |
   | Modbus TCP Port | `502` | Default is 502 |
   | Slave ID | `255` | Check your meter's Modbus settings |

4. Click **Submit**. The integration tests the connection before saving.
5. Repeat for each meter.

## Sensor naming

Sensors follow the pattern `<Meter Name> <Measurement>`, e.g.:

- `DB-1 Voltage L1-N`
- `DB-1 Active Power`
- `DB-1 Active Energy Delivered`

## Polling intervals

- Most sensors: every **5 seconds**
- Energy counters (kWh): every **60 seconds**

## Requirements

- Home Assistant 2023.6 or newer
- `pymodbus >= 3.6.9` (installed automatically)
- Meter must be reachable over Modbus TCP from the HA host
