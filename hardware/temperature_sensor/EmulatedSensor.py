import random

class EmulatedSensor:
    """
    Simple simulation of a water boiler which can heat up water
    and where the heat dissipates slowly over time
    """

    def __init__(self, state):
        self.state = state
        self.state['water_temp'] = 20.0

        self.ambient_temperature = 18.0

    def add_energy(self, degrees):
        self.state['water_temp'] += degrees

    def get_temp_c(self):
        if random.randint(0,4) == 0:
            # some heat dissipation
            dt = self.state['water_temp'] - self.ambient_temperature
            self.state['water_temp'] -= dt / 100

        return self.state['water_temp']
