from utils import topics, PubSub
from coroutines import Base


class SteamControlSignal(Base):
    def __init__(self, hub, default_setpoint=139.5, default_delta=.5):
        super().__init__(hub)

        self.define_ivar("setpoint", topics.TOPIC_STEAM_TEMPERATURE_SET_POINT, default_setpoint, True)
        self.define_ivar("delta", topics.TOPIC_STEAM_TEMPERATURE_DELTA, default_delta, True)

    async def update_steam_control(self):
        with PubSub.Subscription(self.hub, topics.TOPIC_AVERAGE_TEMPERATURE) as queue:
            while True:
                avgtemp = await queue.get()

                high_temp = self.setpoint + self.delta
                low_temp = self.setpoint - self.delta

                if avgtemp < low_temp:
                    self.hub.publish(topics.TOPIC_STEAM_HE_ON, True)
                if avgtemp > high_temp:
                    self.hub.publish(topics.TOPIC_STEAM_HE_ON, False)

    def futures(self, loop):
        return [*super(SteamControlSignal, self).futures(loop), self.update_steam_control()]