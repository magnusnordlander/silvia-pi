import asyncio
from utils import topics, ResizableRingBuffer, PubSub


class BrewControl:
    def __init__(self, hub):
        self.hub = hub

    async def start_brew(self):
        with PubSub.Subscription(self.hub, topics.TOPIC_START_BREW) as queue:
            while True:
                await queue.get()
                self.hub.publish(topics.TOPIC_SOLENOID_OPEN, True)
                self.hub.publish(topics.TOPIC_PUMP_ON, True)

    async def stop_brew(self):
        with PubSub.Subscription(self.hub, topics.TOPIC_STOP_BREW) as queue:
            while True:
                await queue.get()
                self.hub.publish(topics.TOPIC_SOLENOID_OPEN, False)
                self.hub.publish(topics.TOPIC_PUMP_ON, False)

    def futures(self):
        return [self.start_brew(), self.stop_brew()]
