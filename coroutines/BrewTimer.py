import asyncio
from utils import topics, PubSub
import time
from coroutines import Base


class BrewTimer(Base):
    def __init__(self, hub):
        super().__init__(hub)
        self.start_time = None

    async def start_brew_timer(self):
        with PubSub.Subscription(self.hub, topics.TOPIC_START_BREW) as queue:
            while True:
                await queue.get()
                self.start_time = time.time()
                self.hub.publish(topics.TOPIC_CURRENT_BREW_START_TIME, self.start_time)

    async def stop_brew_timer(self):
        with PubSub.Subscription(self.hub, topics.TOPIC_STOP_BREW) as queue:
            while True:
                await queue.get()
                try:
                    duration = time.time() - self.start_time
                except TypeError:
                    continue
                self.start_time = None
                self.hub.publish(topics.TOPIC_CURRENT_BREW_START_TIME, None)
                self.hub.publish(topics.TOPIC_LAST_BREW_DURATION, duration)

    async def update_current_brew_duration(self):
        while True:
            if self.start_time:
                self.hub.publish(topics.TOPIC_CURRENT_BREW_TIME_UPDATE, time.time() - self.start_time)
            await asyncio.sleep(1)

    def futures(self, loop):
        return [self.start_brew_timer(), self.stop_brew_timer(), self.update_current_brew_duration()]
