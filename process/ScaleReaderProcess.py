import sys
from time import sleep, time
from math import isnan
from multiprocessing import Process
from utils import ResizableRingBuffer

class ScaleReaderProcess(Process):
    def __init__(self, state, scale, fast_sample_time):
        super(ScaleReaderProcess, self).__init__()

        self.state = state
        self.scale = scale
        self.sample_time = fast_sample_time

    def run(self):
        i=0
        lasttime = time()

        while True:
            if self.state['keep_scale_connected'] and not self.scale.is_connected():
                self.scale.connect()
                sleep(1)
                lasttime = time()
                continue

            if not self.state['keep_scale_connected'] and self.scale.is_connected():
                self.scale.disconnect()

            if self.scale.is_connected:
                self.state['scale_weight'] = self.scale.weight()
            else:
                self.state['scale_weight'] = None

            sleeptime = lasttime + self.sample_time - time()
            if sleeptime < 0:
                sleeptime = 0
            sleep(sleeptime)
            i += 1
            lasttime = time()

