import asyncio
from utils import topics, PubSub


class HeatingElementController:
    def __init__(self, hub, boiler):
        self.boiler = boiler
        self.hub = hub
        self.steam_mode = False
        self.he_enabled = False

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

    async def update_steam_mode(self):
        with PubSub.Subscription(self.hub, topics.TOPIC_STEAM_MODE) as queue:
            while True:
                self.steam_mode = await queue.get()

    async def update_he_enabled(self):
        with PubSub.Subscription(self.hub, topics.TOPIC_HE_ENABLED) as queue:
            while True:
                self.he_enabled = await queue.get()

    def futures(self):
        return [
            self.update_he_from_steam(),
            self.update_he_from_pid(),
            self.update_steam_mode(),
            self.update_he_enabled(),
        ]