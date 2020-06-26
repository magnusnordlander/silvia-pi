import board
import busio
import digitalio
import random

from adafruit_max31865_fork import MAX31865


class Max31865Sensor(object):
    def __init__(self, cs_boiler, cs_group, clock=board.SCK, mosi=board.MOSI, miso=board.MISO, wires=2, rtd_nominal_boiler=100, rtd_nominal_group=100):
        # Initialize SPI bus and sensor.
        spi = busio.SPI(clock, MOSI=mosi, MISO=miso)
        cs_boiler_io = digitalio.DigitalInOut(cs_boiler)  # Chip select of the MAX31865 board.
        cs_group_io = digitalio.DigitalInOut(cs_group)
        self.boiler_sensor = MAX31865(spi, cs_boiler, rtd_nominal=rtd_nominal_boiler, wires=wires, filter_frequency=50)
        self.group_sensor = MAX31865(spi, cs_boiler, rtd_nominal=rtd_nominal_group, wires=wires, filter_frequency=50)

    def get_update_delay(self):
        return 0.150

    async def get_temp_c(self):
        temp_boiler = await self.boiler_sensor.temperature
        temp_group = await self.group_sensor.temperature

        # I've been getting weird readings of > 700 degrees.
        # Obviously that's not right, let's try to learn more about that
        if temp_boiler > 400:
            if random.randint(0, 100) == 0:
                print("Temperature fault: {}".format(self.boiler_sensor.fault))

        return temp_boiler, temp_group
