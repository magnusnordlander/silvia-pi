import time


class EmulatedBoiler(object):
    """
    Fake water boiler that just logs
    """

    def __init__(self, sensor):
        self.sensor = sensor
        self.last_heat_start = None
        self.last_mode = False
        pass

    def __del__(self):
        self.cleanup()

    def heat_on(self):
        if self.last_mode == False:
            print("Heat on")
        self.last_mode = True
        if self.last_heat_start is None:
            self.last_heat_start = time.time_ns()

        self.update_heat()

    def heat_off(self):
        if self.last_mode == True:
            print("Heat off")
        self.last_mode = False
        self.update_heat()
        self.last_heat_start = None

    def update_heat(self):
        if self.last_heat_start:
            now = time.time_ns()
            diff = now - self.last_heat_start

            self.sensor.add_energy(diff / 200000000)
            self.last_heat_start = now

    def cleanup(self):
        print("Cleaning up")
