class EmulatedSensor:
    """
    Simple simulation of a water boiler which can heat up water
    and where the heat dissipates slowly over time
    """

    def __init__(self, state):
        self.state = state
        self.state['water_temp'] = 20.0

    def add_energy(self, degrees):
        print("Adding energy: ", degrees)
        self.state['water_temp'] += degrees

    def get_temp_c(self):
        return self.state['water_temp']
