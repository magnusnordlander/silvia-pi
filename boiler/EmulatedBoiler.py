import time


class EmulatedBoiler(object):
    """
    Fake water boiler that just logs
    """

    def __init__(self, sensor):
        self.sensor = sensor
        self.last_heat_start = None
        pass

    def __del__(self):
        self.cleanup()

    def heat_on(self):
        print("Heat on")
        if self.last_heat_start is None:
          self.last_heat_start = time.time_ns()

        self.update_heat()

    def heat_off(self):
        print("Heat off")
        self.update_heat()
        self.last_heat_start = None

    def update_heat(self):
        if self.last_heat_start:
            now = time.time_ns()
            diff = now - self.last_heat_start

            self.sensor.add_energy(diff/1000000000)
            self.last_heat_start = now
        else:
            self.sensor.add_energy(-2)

    def cleanup(self):
        print("Cleaning up")