import sys
from time import sleep, time
from math import isnan
from multiprocessing import Process


class SteamControlProcess(Process):
    def __init__(self, state, sample_time, low_temp=139, high_temp=140):
        super(SteamControlProcess, self).__init__()

        self.state = state
        self.sample_time = sample_time
        self.low_temp = low_temp
        self.high_temp = high_temp

    def run(self):
        state = self.state

        steam_low_temp = self.low_temp
        steam_high_temp = self.high_temp
        sample_time = self.sample_time

        lasttime = time()
        j = 0

        while True:  # Loops 10x/second
            avgtemp = self.state['avgtemp']

            if j % 10 == 0:
                if avgtemp < steam_low_temp:
                    state['steam_element_on'] = True
                if avgtemp > steam_high_temp:
                    state['steam_element_on'] = False

            state['j'] = j

            sleeptime = lasttime + sample_time - time()
            if sleeptime < 0:
                sleeptime = 0
            sleep(sleeptime)
            j += 1
            lasttime = time()
