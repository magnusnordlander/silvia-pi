import sys
from time import sleep, time
from math import isnan
import PID as PID
from multiprocessing import Process


class GPLPidprocess(Process):
    def __init__(self, state, temperature_sensor, conf):
        super(GPLPidprocess, self).__init__()

        self.temperature_sensor = temperature_sensor
        self.state = state
        self.conf = conf

    def run(self):
        conf = self.conf
        state = self.state
        sensor = self.temperature_sensor

        pid = PID.PID(conf.Pc,conf.Ic,conf.Dc)
        pid.SetPoint = state['settemp']
        pid.setSampleTime(conf.sample_time*5)

        nanct=0
        i=0
        j=0
        pidhist = [0.,0.,0.,0.,0.,0.,0.,0.,0.,0.]
        avgpid = 0.
        temphist = [0.,0.,0.,0.,0.]
        avgtemp = 0.
        lastsettemp = state['settemp']
        lasttime = time()
        sleeptime = 0
        iscold = True
        iswarm = False
        lastcold = 0
        lastwarm = 0

        try:
            while True:  # Loops 10x/second
                tempc = sensor.get_temp_c()
                if isnan(tempc):
                    nanct += 1
                    if nanct > 100000:
                        sys.exit()
                    continue
                else:
                    nanct = 0

                temphist[i%5] = tempc
                avgtemp = sum(temphist)/len(temphist)

                if avgtemp < 40 :
                    lastcold = i

                if avgtemp > 90 :
                    lastwarm = i

                if iscold and (i-lastcold)*conf.sample_time > 60*15 :
                    pid = PID.PID(conf.Pw,conf.Iw,conf.Dw)
                    pid.SetPoint = state['settemp']
                    pid.setSampleTime(conf.sample_time*5)
                    iscold = False

                if iswarm and (i-lastwarm)*conf.sample_time > 60*15 :
                    pid = PID.PID(conf.Pc,conf.Ic,conf.Dc)
                    pid.SetPoint = state['settemp']
                    pid.setSampleTime(conf.sample_time*5)
                    iscold = True

                if state['settemp'] != lastsettemp :
                    pid.SetPoint = state['settemp']
                    lastsettemp = state['settemp']

                if i%10 == 0 :
                    pid.update(avgtemp)
                    pidout = pid.output
                    pidhist[int(i/10%10)] = pidout
                    avgpid = sum(pidhist)/len(pidhist)

                state['i'] = i
                state['tempc'] = round(tempc,2)
                state['avgtemp'] = round(avgtemp,2)
                state['pidval'] = round(pidout,2)
                state['avgpid'] = round(avgpid,2)
                state['pterm'] = round(pid.PTerm,2)
                if iscold :
                    state['iterm'] = round(pid.ITerm * conf.Ic,2)
                    state['dterm'] = round(pid.DTerm * conf.Dc,2)
                else :
                    state['iterm'] = round(pid.ITerm * conf.Iw,2)
                    state['dterm'] = round(pid.DTerm * conf.Dw,2)
                state['iscold'] = iscold

                print(time(), state)

                sleeptime = lasttime+conf.sample_time-time()
                if sleeptime < 0 :
                    sleeptime = 0
                sleep(sleeptime)
                i += 1
                lasttime = time()

        finally:
            pid.clear()
