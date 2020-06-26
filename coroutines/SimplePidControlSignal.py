import asyncio
from utils import topics, PubSub
import simple_pid_fork
from utils import ResizableRingBuffer
from coroutines import Base


class SimplePidControlSignal(Base):
    def __init__(self, hub, default_tunings, temperature_update_interval=0.25, default_setpoint=105, default_responsiveness=10):
        super().__init__(hub)
        self.temperature_update_interval = temperature_update_interval
        self.define_ivar('tunings', topics.TOPIC_PID_TUNINGS, default_tunings, True)
        self.define_ivar('responsiveness', topics.TOPIC_PID_RESPONSIVENESS, default_responsiveness, True)
        self.define_ivar('avgtemp', topics.TOPIC_AVERAGE_BOILER_TEMPERATURE, default=20)
        self.define_ivar('setpoint', topics.TOPIC_SET_POINT, default=default_setpoint, authoritative=True)

    async def update_pid_control(self):
        pid = simple_pid_fork.PID(setpoint=self.setpoint, windup_limits=(-20, 20))
        pid.tunings = self.tunings
        pid.sample_time = self.temperature_update_interval

        loop = asyncio.get_running_loop()

        pidhist = ResizableRingBuffer(self.responsiveness)
        last_advice = 0

        try:
            with PubSub.Subscription(self.hub, topics.TOPIC_AVERAGE_BOILER_TEMPERATURE) as queue:
                while True:
                    avgtemp = await queue.get()

                    if self.setpoint != pid.setpoint:
                        pid.setpoint = self.setpoint

                    if self.tunings != pid.tunings:
                        pid.tunings = self.tunings

                    if self.responsiveness != pidhist.size_max:
                        pidhist.resize(self.responsiveness)

                    pidout = pid(avgtemp)
                    pidhist.append(pidout)
                    avgpid = pidhist.avg()

                    self.hub.publish(topics.TOPIC_PID_VALUE, pidout)
                    self.hub.publish(topics.TOPIC_PID_TERMS, pid.factored_components)

                    now = loop.time()
                    # We only want to advise the HE Controller to update once per second
                    if now > last_advice + 1:
                        last_advice = now
                        self.hub.publish(topics.TOPIC_PID_AVERAGE_VALUE, avgpid)

        finally:
            pid.reset()

    def futures(self, loop):
        return [
            *super(SimplePidControlSignal, self).futures(loop),
            self.update_pid_control()
        ]
