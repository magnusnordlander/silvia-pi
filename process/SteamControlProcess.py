import sys
from time import sleep, time
from math import isnan
from multiprocessing import Process


class SteamControlProcess(Process):
    def __init__(self, state, temperature_sensor, sample_time, low_temp=139, high_temp=140):
        super(SteamControlProcess, self).__init__()

        self.temperature_sensor = temperature_sensor
        self.state = state
        self.sample_time = sample_time
        self.low_temp = low_temp
        self.high_temp = high_temp

    def run(self):
        state = self.state
        sensor = self.temperature_sensor

        steam_low_temp = self.low_temp
        steam_high_temp = self.high_temp
        sample_time = self.sample_time

        lasttime = time()
        temphist = [0.,0.,0.,0.,0.]
        avgtemp = 0.
        j = 0

        while True:  # Loops 10x/second
            tempc = sensor.get_temp_c()
            if isnan(tempc):
                nanct += 1
                if nanct > 100000:
                    sys.exit()
                continue
            else:
                nanct = 0

            temphist[j % 5] = tempc
            avgtemp = sum(temphist) / len(temphist)

            if j % 10 == 0:
                if avgtemp < steam_low_temp:
                    state['steam_element_on'] = True
                if avgtemp > steam_high_temp:
                    state['steam_element_on'] = False

            state['j'] = j

            print(state)

            sleeptime = lasttime + sample_time - time()
            if sleeptime < 0:
                sleeptime = 0
            sleep(sleeptime)
            j += 1
            lasttime = time()
