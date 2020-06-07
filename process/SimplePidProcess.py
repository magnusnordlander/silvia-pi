import sys
from time import sleep, time
from math import isnan
import simple_pid_fork
from multiprocessing import Process
from utils.const import *

class SimplePidProcess(Process):
    def __init__(self, state, sample_time, conf):
        super(SimplePidProcess, self).__init__()

        self.state = state
        self.sample_time = sample_time
        self.conf = conf

    def run(self):
        conf = self.conf
        state = self.state

        tunings = self.get_tunings()

        pid = simple_pid_fork.PID(setpoint=state['settemp'], windup_limits=(-20, 20))
        pid.tunings = tunings
        pid.sample_time = self.sample_time*5

        i=0
        pidhist = [0.,0.,0.,0.,0.,0.,0.,0.,0.,0.]
        avgpid = 0.
        previous_setpoint = state['settemp']
        lasttime = time()
        previous_tunings = tunings

        try:
            while True:  # Loops 10x/second
                avgtemp = self.state['avgtemp']

                if avgtemp is None:
                    sleep(1)
                    continue

                tunings = self.get_tunings()
                if tunings != previous_tunings:
                    print("Changing tunings to ", tunings)
                    pid.tunings = tunings
                    previous_tunings = tunings

                if state['settemp'] != previous_setpoint:
                    print("Changing set point")
                    pid.setpoint = state['settemp']
                    previous_setpoint = state['settemp']

                if i % 10 == 0:
                    pidout = pid(avgtemp)
                    pidhist[int(i/10%10)] = pidout
                    avgpid = sum(pidhist)/len(pidhist)

                state['i'] = i
                state['pidval'] = round(pidout, 2)
                state['avgpid'] = round(avgpid, 2)
                state['pterm'] = round(pid._proportional, 2)
                state['iterm'] = round(pid._integral, 2)
                state['dterm'] = round(pid._derivative, 2)

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
