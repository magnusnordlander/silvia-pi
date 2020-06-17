import asyncio
from utils import topics, PubSub


class ButtonControls:
    def __init__(self, hub):
        self.hub = hub

    async def update_steam_mode(self):
        with PubSub.Subscription(self.hub, topics.TOPIC_STEAM_BUTTON) as queue:
            while True:
                steam_button = await queue.get()
                self.hub.publish(topics.TOPIC_STEAM_MODE, steam_button)

    async def start_stop_brewing(self):
        with PubSub.Subscription(self.hub, topics.TOPIC_COFFEE_BUTTON) as queue:
            while True:
                coffee_button = await queue.get()
                if coffee_button:
                    self.hub.publish(topics.TOPIC_START_BREW, None)
                else:
                    self.hub.publish(topics.TOPIC_STOP_BREW, None)

    async def start_stop_pump(self):
        with PubSub.Subscription(self.hub, topics.TOPIC_WATER_BUTTON) as queue:
            while True:
                water_button = await queue.get()
                self.hub.publish(topics.TOPIC_PUMP_ON, water_button)

    def futures(self):
        return [self.update_steam_mode(), self.start_stop_brewing(), self.start_stop_pump()]
