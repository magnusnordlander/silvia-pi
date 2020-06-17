import asyncio
from utils import topics, ResizableRingBuffer, PubSub


class BrewControl:
    def __init__(self, hub, default_use_preinfusion=False, default_preinfusion_time=1.2, default_dwell_time=2.5):
        self.hub = hub
        self.use_preinfusion = default_use_preinfusion
        self.preinfusion_time = default_preinfusion_time
        self.dwell_time = default_dwell_time

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

    async def update_use_preinfusion(self):
        with PubSub.Subscription(self.hub, topics.TOPIC_USE_PREINFUSION) as queue:
            while True:
                self.use_preinfusion = await queue.get()

    async def update_preinfusion_time(self):
        with PubSub.Subscription(self.hub, topics.TOPIC_PREINFUSION_TIME) as queue:
            while True:
                self.preinfusion_time = await queue.get()

    async def update_dwell_time(self):
        with PubSub.Subscription(self.hub, topics.TOPIC_DWELL_TIME) as queue:
            while True:
                self.dwell_time = await queue.get()

    def futures(self):
        return [
            self.start_brew(),
            self.stop_brew(),
            self.update_use_preinfusion(),
            self.update_preinfusion_time(),
            self.update_dwell_time()
        ]
