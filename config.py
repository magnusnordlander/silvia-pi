#!/usr/bin/python

import sys
from utils.const import *

# Raspberry Pi SPI Port and Device
spi_port = 0
spi_dev = 0

pigpio_host = "192.168.10.108"
pigpio_port = 8888

test_hardware = sys.platform == "darwin"

# Pin numbers for stuff
try:
    import board

    boiler_temp_sensor_cs_pin = board.D13
    group_temp_sensor_cs_pin = board.D26

    he_pin = 15  # Gray
    solenoid_pin = 14  # Black
    pump_pin = 4  # White

    brew_button_pin = 27
    steam_button_pin = 5
    water_button_pin = 6

    red_button_pin = 23
    blue_button_pin = 24
    white_button_pin = 25
except NotImplementedError:
    boiler_temp_sensor_cs_pin = None
    group_temp_sensor_cs_pin = None
    he_pin = 15  # Gray
    solenoid_pin = 14  # Black
    pump_pin = 4  # White

    brew_button_pin = 27
    steam_button_pin = 5
    water_button_pin = 6

    red_button_pin = 23
    blue_button_pin = 24
    white_button_pin = 25

brew_profile_directory = "/Users/magnusnordlander/brews/" if sys.platform == "darwin" else "/home/pi/brews/"

# Weighted shots
acaia_mac = "9B0F0A71-568C-4DB5-9002-F1D09B240D0A" if sys.platform == "darwin" else "00:1c:97:1a:a0:2f"
weighted_shot_reaction_time = 0.5  # seconds

default_target_ratio = 2.0

# Default temperatures
set_point = 105.
steam_set_point = 139.5
steam_delta = .5

# Pre-infusion settings
use_preinfusion = False  # Just a default
preinfusion_time = 1.2
dwell_time = 2.5

# PID Proportional, Integral, and Derivative values
use_pump_tunings = True

tunings = {
    TUNINGS_COLD: {
        KP: 3.4,
        KI: 0.3,
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

mqtt_server = "192.168.10.66"
mqtt_prefix = "fakesilvia/" if sys.platform == "darwin" else "silvia/"
