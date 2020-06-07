#!/usr/bin/python

from utils.const import *

# Raspberry Pi SPI Port and Device
spi_port = 0
spi_dev = 0

test_hardware = False

# Pin numbers for stuff
try:
    import board

    temp_sensor_cs_pin = board.D5
    he_pin = 18
    solenoid_pin = 14
    pump_pin = 15

    brew_button_pin = 21
    steam_button_pin = 16
    water_button_pin = 20
except NotImplementedError:
    temp_sensor_cs_pin = None
    he_pin = None
    solenoid_pin = None
    brew_button_pin = 21
    steam_button_pin = 16
    water_button_pin = 20

# Weighted shots
acaia_mac = "00:1c:97:1a:a0:2f"
weighted_shot_reaction_compensation = -2  #grams
disable_buttons_during_weighted_shot = True

# Default temperatures
set_temp = 105.
steam_low_temp = 139.
steam_high_temp = 140.

# Pre-infusion settings
use_preinfusion = False  # Just a default
preinfusion_time = 1.2
dwell_time = 2.5

# Main loop sample rate in seconds
fast_sample_time = 0.01
slow_sample_time = 0.1
factor = 10

# PID Proportional, Integral, and Derivative values
use_pump_tunings = True

tunings = {
    TUNINGS_COLD: {
        KP: 3.4,
        KI: 0.3,  # Traditional I multiplied by slow_sample_time
        KD: 40.0,
        RESPONSIVENESS: 10 # Lower is more responsive
    },
    TUNINGS_WARM: {
        KP: 4.0,
        KI: 0.2,
        KD: 40.0,
        RESPONSIVENESS: 10  # Lower is more responsive
    },
    TUNINGS_PUMPING: {
        KP: 5,
        KI: 0.3,
        KD: 40.0,
        RESPONSIVENESS: 3
    },
}

#Web/REST Server Options
port = 8080

mqtt_server = "192.168.10.66"
mqtt_prefix = "fakesilvia"
