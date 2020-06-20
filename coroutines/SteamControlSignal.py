from utils import topics, PubSub
from coroutines import Base


class SteamControlSignal(Base):
    def __init__(self, hub, low_temp=139, high_temp=140):
        super().__init__(hub)
        self.high_temp = high_temp
        self.low_temp = low_temp

    async def update_steam_control(self):
        with PubSub.Subscription(self.hub, topics.TOPIC_AVERAGE_TEMPERATURE) as queue:
            while True:
                avgtemp = await queue.get()
                if avgtemp < self.low_temp:
                    self.hub.publish(topics.TOPIC_STEAM_HE_ON, True)
                if avgtemp > self.high_temp:
                    self.hub.publish(topics.TOPIC_STEAM_HE_ON, False)

    def futures(self, loop):
        return [self.update_steam_control()]