import asyncio
from utils import topics, ResizableRingBuffer, PubSub
import time


class BrewTimer:
    def __init__(self, hub):
        self.hub = hub
        self.start_time = None

    async def start_brew_timer(self):
        with PubSub.Subscription(self.hub, topics.TOPIC_START_BREW) as queue:
            while True:
                await queue.get()
                self.start_time = time.time()

    async def stop_brew_timer(self):
        with PubSub.Subscription(self.hub, topics.TOPIC_STOP_BREW) as queue:
            while True:
                await queue.get()
                try:
                    duration = time.time() - self.start_time
                except TypeError:
                    continue
                self.start_time = None
                self.hub.publish(topics.TOPIC_LAST_BREW_DURATION, duration)

    def futures(self):
        return [self.start_brew_timer(), self.stop_brew_timer()]
