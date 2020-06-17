import board
import busio
import digitalio

from adafruit_max31865_fork import MAX31865


class Max31865Sensor(object):
    def __init__(self, cs, clock=board.SCK, mosi=board.MOSI, miso=board.MISO, wires=2, rtd_nominal=100):
        # Initialize SPI bus and sensor.
        spi = busio.SPI(clock, MOSI=mosi, MISO=miso)
        cs = digitalio.DigitalInOut(cs)  # Chip select of the MAX31865 board.
        self.sensor = MAX31865(spi, cs, rtd_nominal=rtd_nominal, wires=wires)

    def get_update_delay(self):
        return 0.075

    async def get_temp_c(self):
        return await self.sensor.temperature
