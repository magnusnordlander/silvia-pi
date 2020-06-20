import asyncio
from utils import topics, PubSub
from coroutines import Base


class BrewControl(Base):
    def __init__(self, hub, default_use_preinfusion=False, default_preinfusion_time=1.2, default_dwell_time=2.5):
        super().__init__(hub)
        self.hub = hub
        self.define_ivar('use_preinfusion', topics.TOPIC_USE_PREINFUSION, default=default_use_preinfusion, authoritative=True)
        self.define_ivar('preinfusion_time', topics.TOPIC_PREINFUSION_TIME, default=default_preinfusion_time, authoritative=True)
        self.define_ivar('dwell_time', topics.TOPIC_DWELL_TIME, default=default_dwell_time, authoritative=True)

    async def start_brew(self):
        with PubSub.Subscription(self.hub, topics.TOPIC_START_BREW) as queue:
            while True:
                await queue.get()
                self.hub.publish(topics.TOPIC_SOLENOID_OPEN, True)
                self.hub.publish(topics.TOPIC_PUMP_ON, True)

                if self.use_preinfusion:
                    await asyncio.sleep(self.preinfusion_time)
                    self.hub.publish(topics.TOPIC_SOLENOID_OPEN, False)
                    self.hub.publish(topics.TOPIC_PUMP_ON, False)

                    await asyncio.sleep(self.dwell_time)
                    self.hub.publish(topics.TOPIC_SOLENOID_OPEN, True)
                    self.hub.publish(topics.TOPIC_PUMP_ON, True)

    async def stop_brew(self):
        with PubSub.Subscription(self.hub, topics.TOPIC_STOP_BREW) as queue:
            while True:
                await queue.get()
                self.hub.publish(topics.TOPIC_SOLENOID_OPEN, False)
                self.hub.publish(topics.TOPIC_PUMP_ON, False)

    def futures(self, loop):
        return [
            *super(BrewControl, self).futures(loop),
            self.start_brew(),
            self.stop_brew(),
        ]
