"""MQTT Topics"""

TOPIC_BUTTON_PROXY = "sensor/button/_proxy"

# Hardware button states
TOPIC_COFFEE_BUTTON = "sensor/button/coffee"
TOPIC_WATER_BUTTON = "sensor/button/water"
TOPIC_STEAM_BUTTON = "sensor/button/steam"

TOPIC_RED_BUTTON = "sensor/button/red"
TOPIC_BLUE_BUTTON = "sensor/button/blue"
TOPIC_WHITE_BUTTON = "sensor/button/white"

# Sensor data
TOPIC_CURRENT_BOILER_TEMPERATURE = "sensor/boiler_temperature"
TOPIC_AVERAGE_BOILER_TEMPERATURE = "sensor/average_boiler_temperature"
TOPIC_CURRENT_GROUP_TEMPERATURE = "sensor/group_temperature"
TOPIC_ALL_TEMPERATURES = "sensor/all_temperatures"
TOPIC_SCALE_WEIGHT = "sensor/scale_weight"

# Does the steam controller want the heating element on?
TOPIC_STEAM_HE_ON = "advice/steam/he_on"

# PID data
TOPIC_PID_VALUE = "advice/pid/pidval"
TOPIC_PID_AVERAGE_VALUE = "advice/pid/avgpid"
TOPIC_PID_TERMS = "advice/pid/terms"

# Something wants us to start/stop the brew
TOPIC_START_BREW = "advice/brew/start"
TOPIC_STOP_BREW = "advice/brew/stop"

TOPIC_CAPTURE_DOSE = "advice/capture_dose"
TOPIC_CAPTURE_DOSE_AND_SET_TARGET_WEIGHT = "advice/capture_dose_and_set_target_weight"
TOPIC_DOSE = "status/dose"
TOPIC_TARGET_RATIO = "status/target_ratio"

# Turn on/off the pump, or open/close the solenoid
TOPIC_PUMP_ON = "actuator/pump"
TOPIC_SOLENOID_OPEN = "actuator/solenoid"

# Probably not necessary, but this means we've sent a heartbeat to the scale
TOPIC_SCALE_HEARTBEAT_SENT = "advice/scale/heartbeat_sent"

# Try to keep the scale connected (or disconnect if this turns false)
TOPIC_CONNECT_TO_SCALE = "advice/scale/keep_connected"
TOPIC_TARGET_WEIGHT = "advice/scale/target_weight"
TOPIC_ENABLE_WEIGHTED_SHOT = "advice/scale/enable_weighted_shot"


TOPIC_SET_POINT = "advice/pid/set_point"
TOPIC_PID_TUNINGS = "advice/pid/tunings"
TOPIC_PID_RESPONSIVENESS = "advice/pid/responsiveness"
TOPIC_PUMP_PIDVAL_FEED_FORWARD = "advice/pid/pump_feed_forward"
TOPIC_STEAM_TEMPERATURE_SET_POINT = "advice/steam_temperature/set_point"
TOPIC_STEAM_TEMPERATURE_DELTA = "advice/steam_temperature/delta"

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

TOPIC_OLED_SAVER = "mode/oled_saver"

TOPIC_LAST_BREW_DURATION = "status/last_brew_duration"
TOPIC_CURRENT_BREW_START_TIME = "status/current_brew_start_time"
TOPIC_CURRENT_BREW_TIME_UPDATE = "status/current_brew_duration"
