import asyncio
from utils import topics, PubSub
import simple_pid_fork
from utils.const import *
from utils import ResizableRingBuffer


class SimplePidControlSignal:
    def __init__(self, hub, temperature_update_interval=0.25):
        self.temperature_update_interval = temperature_update_interval
        self.setpoint = 105
        self.tunings = (3.4, 0.3, 40.0)
        self.responsiveness = 10
        self.hub = hub
        self.avgtemp = 20

    async def update_avg_temp(self):
        with PubSub.Subscription(self.hub, topics.TOPIC_AVERAGE_TEMPERATURE) as queue:
            while True:
                self.avgtemp = await queue.get()

    async def update_pid_control(self):
        pid = simple_pid_fork.PID(setpoint=self.setpoint, windup_limits=(-20, 20))
        pid.tunings = self.tunings
        pid.sample_time = self.temperature_update_interval

        loop = asyncio.get_running_loop()

        pidout = 0
        pidhist = ResizableRingBuffer(self.responsiveness)
        avgpid = 0.
        previous_setpoint = self.setpoint
        previous_tunings = self.tunings
        previous_responsiveness = self.responsiveness
        last_advice = 0

        try:
            with PubSub.Subscription(self.hub, topics.TOPIC_AVERAGE_TEMPERATURE) as queue:
                while True:
                    avgtemp = await queue.get()

                    pidout = pid(avgtemp)
                    pidhist.append(pidout)
                    avgpid = pidhist.avg()
                    #print("T: {}, PID: {}, <PID>: {}, Terms: {}".format(avgtemp, pidout, avgpid, pid.components))

                    self.hub.publish(topics.TOPIC_PID_VALUE, pidout)

                    now = loop.time()
                    # We only want to advise the HE Controller to update once per second
                    if now > last_advice + 1:
                        last_advice = now
                        self.hub.publish(topics.TOPIC_PID_AVERAGE_VALUE, avgpid)
#                    state['pterm'] = round(pid._proportional, 2)
#                    state['iterm'] = round(pid._integral * pid.Ki, 2)
#                    state['dterm'] = round(pid._derivative * -pid.Kd, 2)

        finally:
            pid.reset()

    def futures(self):
        return [self.update_pid_control(), self.update_avg_temp()]
