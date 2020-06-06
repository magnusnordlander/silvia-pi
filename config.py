#!/usr/bin/python

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
    brew_button_pin = 21
except NotImplementedError:
    temp_sensor_cs_pin = None
    he_pin = None
    solenoid_pin = None
    brew_button_pin = None

# Default temperatures
set_temp = 105.
steam_low_temp = 139.
steam_high_temp = 140.

# Main loop sample rate in seconds
fast_sample_time = 0.001
slow_sample_time = 0.1
factor = 100

# PID Proportional, Integral, and Derivative values
Pc = 3.4
Ic = 0.3
Dc = 40.0

Pw = 2.9
Iw = 0.3
Dw = 40.0

#Web/REST Server Options
port = 8080

mqtt_server = "192.168.10.66"
mqtt_prefix = "silvia"
