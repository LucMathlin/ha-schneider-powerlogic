"""Constants for the Schneider PowerLogic Modbus integration."""

DOMAIN = "schneider_powerlogic"

CONF_SLAVE = "slave"
CONF_NAME = "name"
CONF_SENSOR_GROUPS = "sensor_groups"
CONF_INVERT_POWER = "invert_power"

DEFAULT_PORT = 502
DEFAULT_SLAVE = 255
DEFAULT_SCAN_INTERVAL = 5

# Sensor group keys
GROUP_ACTIVE_POWER   = "active_power"
GROUP_VOLTAGE        = "voltage"
GROUP_CURRENT        = "current"
GROUP_REACTIVE_POWER = "reactive_power"
GROUP_POWER_FACTOR   = "power_factor"
GROUP_ENERGY         = "energy"
GROUP_TEMPERATURE    = "temperature"
GROUP_THD            = "thd"

# Groups that are enabled by default (active power is always on and not shown as a checkbox)
SENSOR_GROUPS = {
    GROUP_ACTIVE_POWER:   "Active Power (per phase + total)",
    GROUP_VOLTAGE:        "Voltages",
    GROUP_CURRENT:        "Currents",
    GROUP_REACTIVE_POWER: "Reactive & Apparent Power",
    GROUP_POWER_FACTOR:   "Power Factor & Frequency",
    GROUP_ENERGY:         "Energy (kWh)",
    GROUP_TEMPERATURE:    "Temperature",
    GROUP_THD:            "THD (Total Harmonic Distortion)",
}

# Active power is mandatory — always included, not shown as a checkbox
MANDATORY_GROUPS = {GROUP_ACTIVE_POWER}

# Sensor keys that get inverted when CONF_INVERT_POWER is enabled
INVERTIBLE_KEYS = {
    "active_power_l1", "active_power_l2", "active_power_l3", "active_power",
    "reactive_power",
}

# Sensor definitions tuple layout:
# (key, label, address, data_type, unit, device_class, state_class, scale, precision, scan_interval, group)

SENSOR_DEFINITIONS = [
    # -------- Voltages --------
    ("voltage_l1_n",    "Voltage L1-N",    3027,  "float32", "V",   "voltage",      "measurement",      None, 2, 5,  GROUP_VOLTAGE),
    ("voltage_l2_n",    "Voltage L2-N",    3029,  "float32", "V",   "voltage",      "measurement",      None, 2, 5,  GROUP_VOLTAGE),
    ("voltage_l3_n",    "Voltage L3-N",    3031,  "float32", "V",   "voltage",      "measurement",      None, 2, 5,  GROUP_VOLTAGE),
    ("voltage_l1_l2",   "Voltage L1-L2",   3019,  "float32", "V",   "voltage",      "measurement",      None, 2, 5,  GROUP_VOLTAGE),
    ("voltage_l2_l3",   "Voltage L2-L3",   3021,  "float32", "V",   "voltage",      "measurement",      None, 2, 5,  GROUP_VOLTAGE),
    ("voltage_l3_l1",   "Voltage L3-L1",   3023,  "float32", "V",   "voltage",      "measurement",      None, 2, 5,  GROUP_VOLTAGE),
    ("voltage_ll_avg",  "Voltage L-L Avg", 3025,  "float32", "V",   "voltage",      "measurement",      None, 2, 5,  GROUP_VOLTAGE),
    ("voltage_ln_avg",  "Voltage L-N Avg", 3035,  "float32", "V",   "voltage",      "measurement",      None, 2, 5,  GROUP_VOLTAGE),
    # -------- Currents --------
    ("current_l1",      "Current L1",      2999,  "float32", "A",   "current",      "measurement",      None, 2, 5,  GROUP_CURRENT),
    ("current_l2",      "Current L2",      3001,  "float32", "A",   "current",      "measurement",      None, 2, 5,  GROUP_CURRENT),
    ("current_l3",      "Current L3",      3003,  "float32", "A",   "current",      "measurement",      None, 2, 5,  GROUP_CURRENT),
    ("current_n",       "Current N",       3005,  "float32", "A",   "current",      "measurement",      None, 2, 5,  GROUP_CURRENT),
    ("current_avg",     "Current Avg",     3009,  "float32", "A",   "current",      "measurement",      None, 2, 5,  GROUP_CURRENT),
    # -------- Active Power --------
    ("active_power_l1", "Active Power L1", 3053,  "float32", "W",   "power",        "measurement",      1000, 2, 5,  GROUP_ACTIVE_POWER),
    ("active_power_l2", "Active Power L2", 3055,  "float32", "W",   "power",        "measurement",      1000, 2, 5,  GROUP_ACTIVE_POWER),
    ("active_power_l3", "Active Power L3", 3057,  "float32", "W",   "power",        "measurement",      1000, 2, 5,  GROUP_ACTIVE_POWER),
    ("active_power",    "Active Power",    3059,  "float32", "W",   "power",        "measurement",      1000, 2, 5,  GROUP_ACTIVE_POWER),
    # -------- Reactive & Apparent Power --------
    ("apparent_power",  "Apparent Power",  3075,  "float32", "VA",  None,           "measurement",      1000, 2, 5,  GROUP_REACTIVE_POWER),
    ("reactive_power",  "Reactive Power",  3067,  "float32", "var", None,           "measurement",      1000, 2, 5,  GROUP_REACTIVE_POWER),
    # -------- Power Factor & Frequency --------
    ("power_factor",    "Power Factor",    3191,  "float32", None,  "power_factor", "measurement",      None, 2, 5,  GROUP_POWER_FACTOR),
    ("frequency",       "Frequency",       3109,  "float32", "Hz",  "frequency",    "measurement",      None, 2, 5,  GROUP_POWER_FACTOR),
    # -------- Temperature --------
    ("temperature",     "Temperature",     3131,  "float32", "°C",  "temperature",  "measurement",      None, 2, 5,  GROUP_TEMPERATURE),
    # -------- Energy --------
    ("energy_delivered","Active Energy Delivered", 2699, "float32", "kWh", "energy", "total_increasing", None, 2, 5, GROUP_ENERGY),
    ("energy_received", "Active Energy Received",  2701, "float32", "kWh", "energy", "total_increasing", None, 2, 5, GROUP_ENERGY),
    # -------- THD --------
    ("thd_voltage_ll",  "THD Voltage L-L", 21327, "float32", "%",   None,           "measurement",      None, 2, 5,  GROUP_THD),
    ("thd_current_l1",  "THD Current L1",  21299, "float32", "%",   None,           "measurement",      None, 2, 5,  GROUP_THD),
    ("thd_current_l2",  "THD Current L2",  21301, "float32", "%",   None,           "measurement",      None, 2, 5,  GROUP_THD),
    ("thd_current_l3",  "THD Current L3",  21303, "float32", "%",   None,           "measurement",      None, 2, 5,  GROUP_THD),
    ("thd_current_n",   "THD Current N",   21305, "float32", "%",   None,           "measurement",      None, 2, 5,  GROUP_THD),
]
