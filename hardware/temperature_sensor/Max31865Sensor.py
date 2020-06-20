import board
import busio
import digitalio
import random

from adafruit_max31865_fork import MAX31865


class Max31865Sensor(object):
    def __init__(self, cs, clock=board.SCK, mosi=board.MOSI, miso=board.MISO, wires=2, rtd_nominal=100):
        # Initialize SPI bus and sensor.
        spi = busio.SPI(clock, MOSI=mosi, MISO=miso)
        cs = digitalio.DigitalInOut(cs)  # Chip select of the MAX31865 board.
        self.sensor = MAX31865(spi, cs, rtd_nominal=rtd_nominal, wires=wires, filter_frequency=50)

    def get_update_delay(self):
        return 0.075

    async def get_temp_c(self):
        temp = await self.sensor.temperature

        # I've been getting weird readings of > 700 degrees.
        # Obviously that's not right, let's try to learn more about that
        if temp > 400:
            if random.randint(0, 100) == 0:
                print("Temperature fault: {}".format(self.sensor.fault))

        return temp
