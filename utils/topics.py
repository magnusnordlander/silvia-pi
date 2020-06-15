"""MQTT Topics"""

TOPIC_BUTTON_PROXY = "sensor/button/_proxy"

# Hardware button states
TOPIC_COFFEE_BUTTON = "sensor/button/coffee"
TOPIC_WATER_BUTTON = "sensor/button/water"
TOPIC_STEAM_BUTTON = "sensor/button/steam"

# Sensor data
TOPIC_CURRENT_TEMPERATURE = "sensor/temperature"
TOPIC_AVERAGE_TEMPERATURE = "sensor/average_temperature"
TOPIC_SCALE_WEIGHT = "sensor/scale_weight"

# Does the steam controller want the heating element on?
TOPIC_STEAM_HE_ON = "advice/steam/he_on"

# PID data
TOPIC_PID_VALUE = "advice/pid/pidval"
TOPIC_PID_AVERAGE_VALUE = "advice/pid/avgpid"
TOPIC_PID_P_TERM = "advice/pid/p_term"
TOPIC_PID_I_TERM = "advice/pid/i_term"
TOPIC_PID_D_TERM = "advice/pid/d_term"

# Something wants us to start/stop the brew
TOPIC_START_BREW = "advice/brew/start"
TOPIC_STOP_BREW = "advice/brew/stop"

# Turn on/off the pump, or open/close the solenoid
TOPIC_PUMP_ON = "actuator/pump"
TOPIC_SOLENOID_OPEN = "actuator/solenoid"

# Probably not necessary, but this means we've sent a heartbeat to the scale
TOPIC_SCALE_HEARTBEAT_SENT = "advice/scale/heartbeat_sent"

# Try to keep the scale connected (or disconnect if this turns false)
TOPIC_CONNECT_TO_SCALE = "advice/scale/keep_connected"
TOPIC_TARGET_WEIGHT = "advice/scale/target_weight"
TOPIC_ENABLE_WEIGHTED_SHOT = "advice/scale/enable_weighted_shot"

TOPIC_SET_POINT = "advice/set_point"

# The scale *is* connected
TOPIC_SCALE_CONNECTED = "mode/scale_connected"

# Informational topic for whether the heating element is on
TOPIC_HE_ON = "status/he_on"

# Authoritative mode for whether the Heating Element Controller should be controlling based on Steam Control inputs
# or PID inputs
TOPIC_STEAM_MODE = "mode/steam_mode"

TOPIC_USE_PREINFUSION = "mode/use_preinfusion"
TOPIC_PREINFUSION_TIME = "mode/use_preinfusion/preinfusion_time"
TOPIC_DWELL_TIME = "mode/use_preinfusion/dwell_time"
TOPIC_HE_ENABLED = "mode/he_enabled"

TOPIC_LAST_BREW_DURATION = "status/last_brew_duration"
TOPIC_CURRENT_BREW_START_TIME = "status/current_brew_start_time"
TOPIC_CURRENT_BREW_TIME_UPDATE = "status/current_brew_duration"
