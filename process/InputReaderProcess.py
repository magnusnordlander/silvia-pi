import sys
from time import sleep, time
from math import isnan
from multiprocessing import Process

class InputReaderProcess(Process):
    def __init__(self, state, temperature_sensor, brew_button, sample_time, temperature_factor):
        super(InputReaderProcess, self).__init__()

        self.temperature_sensor = temperature_sensor
        self.brew_button = brew_button
        self.sample_time = sample_time
        self.temperature_factor = temperature_factor
        self.state = state

    def run(self):
        temphist = [0.,0.,0.,0.,0.]
        i=0
        j=0
        lasttime = time()

        while True:
            self.state['brew_button'] = self.brew_button.button_state()

            if i % self.temperature_factor == 0:
                tempc = self.temperature_sensor.get_temp_c()
                if isnan(tempc):
                    nanct += 1
                    if nanct > 100000:
                        sys.exit()
                    continue
                else:
                    nanct = 0

                temphist[j % 5] = tempc
                self.state['tempc'] = round(tempc, 2)
                self.state['avgtemp'] = round(sum(temphist) / len(temphist), 2)
                j += 1

            sleeptime = lasttime + self.sample_time - time()
            if sleeptime < 0:
                sleeptime = 0
            sleep(sleeptime)
            i += 1
            lasttime = time()