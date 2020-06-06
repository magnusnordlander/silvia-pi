import sys
from time import sleep, time
from math import isnan
from multiprocessing import Process

class SensorReaderProcess(Process):
    def __init__(self, state, temperature_sensor, sample_time):
        super(SensorReaderProcess, self).__init__()

        self.temperature_sensor = temperature_sensor
        self.sample_time = sample_time
        self.state = state

    def run(self):
        temphist = [0.,0.,0.,0.,0.]
        avgtemp = 0.
        i=0
        lasttime = time()

        while True:  # Loops 10x/second
            tempc = self.temperature_sensor.get_temp_c()
            if isnan(tempc):
                nanct += 1
                if nanct > 100000:
                    sys.exit()
                continue
            else:
                nanct = 0

            temphist[i % 5] = tempc
            avgtemp = sum(temphist) / len(temphist)

            self.state['tempc'] = round(tempc, 2)
            self.state['avgtemp'] = round(avgtemp, 2)

            print(self.state)

            sleeptime = lasttime + self.sample_time - time()
            if sleeptime < 0:
                sleeptime = 0
            sleep(sleeptime)
            i += 1
            lasttime = time()