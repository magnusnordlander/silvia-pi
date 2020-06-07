from time import sleep, time
import simple_pid_fork
from multiprocessing import Process
from utils.const import *
from utils import ResizableRingBuffer

class SimplePidProcess(Process):
    def __init__(self, state, sample_time, conf):
        super(SimplePidProcess, self).__init__()

        self.state = state
        self.sample_time = sample_time
        self.conf = conf

    def run(self):
        state = self.state

        tunings = self.get_tunings()
        responsiveness = self.get_responsiveness()

        pid = simple_pid_fork.PID(setpoint=state['settemp'], windup_limits=(-20, 20))
        pid.tunings = tunings
        pid.sample_time = self.sample_time*5

        i=0
        pidout = 0
        pidhist = ResizableRingBuffer(responsiveness)
        avgpid = 0.
        previous_setpoint = state['settemp']
        lasttime = time()
        previous_tunings = tunings
        previous_responsiveness = responsiveness

        try:
            while True:  # Loops 10x/second
                avgtemp = self.state['avgtemp']

                if avgtemp is None:
                    sleep(1)
                    continue

                if i % 10 == 0:
                    tunings = self.get_tunings()
                    if tunings != previous_tunings:
                        print("Changing tunings to ", tunings)
                        pid.tunings = tunings
                        previous_tunings = tunings

                    if state['settemp'] != previous_setpoint:
                        print("Changing set point")
                        pid.setpoint = state['settemp']
                        previous_setpoint = state['settemp']

                    responsiveness = self.get_responsiveness()
                    if responsiveness != previous_responsiveness:
                        print("Changing responsiveness to ", responsiveness)
                        pidhist.resize(responsiveness)
                        previous_responsiveness = responsiveness

                    pidout = pid(avgtemp)
                    pidhist.append(pidout)
                    avgpid = pidhist.avg()

                state['i'] = i
                state['pidval'] = round(pidout, 2)
                state['avgpid'] = round(avgpid, 2)
                state['pterm'] = round(pid._proportional, 2)
                state['iterm'] = round(pid._integral * pid.Ki, 2)
                state['dterm'] = round(pid._derivative * -pid.Kd, 2)

                sleeptime = lasttime+self.sample_time-time()
                if sleeptime < 0:
                    sleeptime = 0
                sleep(sleeptime)
                i += 1
                lasttime = time()

        finally:
            pid.reset()

    def get_tunings(self):
        tunings = self.state['tunings']

        if tunings == TUNINGS_DYNAMIC:
            return self.state['dynamic_kp'], self.state['dynamic_kd'], self.state['dynamic_kd']

        try:
            return self.conf.tunings[tunings][KP], self.conf.tunings[tunings][KI], self.conf.tunings[tunings][KD]
        except KeyError:
            return 2.9, 0.3, 40.

    def get_responsiveness(self):
        tunings = self.state['tunings']

        if tunings == TUNINGS_DYNAMIC:
            return self.state['dynamic_responsiveness']

        try:
            return self.conf.tunings[tunings][RESPONSIVENESS]
        except KeyError:
            return 10
