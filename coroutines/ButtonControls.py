from utils import topics, PubSub
from coroutines import Base


class ButtonControls(Base):
    def __init__(self, hub):
        super().__init__(hub)

        self.define_ivar('keep_scale_connected', topics.TOPIC_CONNECT_TO_SCALE, False)
        self.define_ivar('enable_weighted_shot', topics.TOPIC_ENABLE_WEIGHTED_SHOT, False)
        self.define_ivar('enable_preinfusion', topics.TOPIC_USE_PREINFUSION, False)

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

    async def red_button_press(self):
        with PubSub.Subscription(self.hub, topics.TOPIC_RED_BUTTON) as queue:
            while True:
                await queue.get()
                self.hub.publish(topics.TOPIC_CONNECT_TO_SCALE, not self.keep_scale_connected)

    async def blue_button_press(self):
        with PubSub.Subscription(self.hub, topics.TOPIC_BLUE_BUTTON) as queue:
            while True:
                await queue.get()
                self.hub.publish(topics.TOPIC_ENABLE_WEIGHTED_SHOT, not self.enable_weighted_shot)

    async def white_button_press(self):
        with PubSub.Subscription(self.hub, topics.TOPIC_WHITE_BUTTON) as queue:
            while True:
                await queue.get()
                self.hub.publish(topics.TOPIC_USE_PREINFUSION, not self.enable_preinfusion)

    def futures(self, loop):
        return [
            *super(ButtonControls, self).futures(loop),
            self.update_steam_mode(),
            self.start_stop_brewing(),
            self.start_stop_pump(),
            self.red_button_press(),
            self.blue_button_press(),
            self.white_button_press(),
        ]
