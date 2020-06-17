import asyncio
from utils import topics, PubSub


class SteamControlSignal:
    def __init__(self, hub, low_temp=139, high_temp=140):
        self.high_temp = high_temp
        self.low_temp = low_temp
        self.hub = hub

    async def update_steam_control(self):
        with PubSub.Subscription(self.hub, topics.TOPIC_AVERAGE_TEMPERATURE) as queue:
            while True:
                avgtemp = await queue.get()
                if avgtemp < self.low_temp:
                    self.hub.publish(topics.TOPIC_STEAM_HE_ON, True)
                if avgtemp > self.high_temp:
                    self.hub.publish(topics.TOPIC_STEAM_HE_ON, False)

    def futures(self):
        return [self.update_steam_control()]