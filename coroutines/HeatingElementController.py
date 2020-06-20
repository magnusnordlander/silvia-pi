import asyncio
from utils import topics, PubSub
from coroutines import Base


class HeatingElementController(Base):
    def __init__(self, hub, boiler):
        super().__init__(hub)
        self.boiler = boiler
        self.define_ivar('steam_mode', topics.TOPIC_STEAM_MODE, default=False, authoritative=True)
        self.define_ivar('he_enabled', topics.TOPIC_HE_ENABLED, default=False, authoritative=True)

    async def update_he_from_pid(self):
        with PubSub.Subscription(self.hub, topics.TOPIC_PID_AVERAGE_VALUE) as queue:
            while True:
                avgpid = await queue.get()
                if not self.steam_mode:
                    if avgpid >= 100 and self.he_enabled:
                        self.he_on()
                        await asyncio.sleep(1)
                    elif 0 < avgpid < 100 and self.he_enabled:
                        self.he_on()
                        await asyncio.sleep(avgpid / 100.)

                        # Just gotta make sure mode didn't change in between.
                        # We don't want to trample the other controller
                        if self.steam_mode:
                            continue

                        self.he_off()
                        await asyncio.sleep(1 - (avgpid / 100.))
                    else:
                        self.he_off()
                        await asyncio.sleep(1)

    def he_on(self):
        self.boiler.heat_on()
        self.hub.debounce_publish(topics.TOPIC_HE_ON, True)

    def he_off(self):
        self.boiler.heat_off()
        self.hub.debounce_publish(topics.TOPIC_HE_ON, False)

    async def update_he_from_steam(self):
        with PubSub.Subscription(self.hub, topics.TOPIC_STEAM_HE_ON) as queue:
            while True:
                steam_he_on = await queue.get()
                if self.steam_mode:
                    if steam_he_on and self.he_enabled:
                        self.boiler.heat_on()
                    else:
                        self.boiler.heat_off()

    def futures(self, loop):
        return [
            *super(HeatingElementController, self).futures(loop),
            self.update_he_from_steam(),
            self.update_he_from_pid(),
        ]