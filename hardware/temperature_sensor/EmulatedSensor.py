import random
import asyncio

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

    def get_update_delay(self):
        return 0.075

    async def get_temp_c(self):
        if random.randint(0,2) == 0:
            # some heat dissipation
            dt = self.state['water_temp'] - self.ambient_temperature
            self.state['water_temp'] -= dt / 300

        await asyncio.sleep(0.075)

        return self.state['water_temp']
