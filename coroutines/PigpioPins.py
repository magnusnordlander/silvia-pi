import asyncio
import apigpio_fork
import config as conf
from utils import topics, PubSub
from functools import partial
from coroutines import Base

@apigpio_fork.Debounce()
def on_input_forward_to_hub(gpio, level, tick, hub, topic, pi):
    hub.publish(topics.TOPIC_BUTTON_PROXY, (gpio, level, tick, topic))


class PigpioPins(Base):
    def __init__(self, hub, loop):
        super().__init__(hub)
        self.loop = loop
        self.pi = apigpio_fork.Pi(self.loop)

    @asyncio.coroutine
    def subscribe_to_pins(self, pi, hub):
        pins = {
            conf.brew_button_pin: topics.TOPIC_COFFEE_BUTTON,
            conf.steam_button_pin: topics.TOPIC_STEAM_BUTTON,
            conf.water_button_pin: topics.TOPIC_WATER_BUTTON,
        }

        for pin in pins:
            yield from pi.set_mode(pin, apigpio_fork.INPUT)
            yield from pi.set_pull_up_down(pin, apigpio_fork.PUD_DOWN)
            yield from pi.set_glitch_filter(pin, 5000)
            yield from pi.add_callback(pin, edge=apigpio_fork.EITHER_EDGE, func=partial(on_input_forward_to_hub, hub=hub, topic=pins[pin], pi=pi))

    async def maybe_update_button(self):
        with PubSub.Subscription(self.hub, topics.TOPIC_BUTTON_PROXY) as queue:
            while True:
                (gpio, level, tick, topic) = await queue.get()
                await asyncio.sleep(0.005)
                new_level = await self.pi.read(gpio)
                if new_level == level:
                    self.hub.publish(topic, level == 1)
                else:
                    print("False button "+topic)

    def pre_futures(self):
        address = ('192.168.10.107', 8888)
        return [self.pi.connect(address)]

    def futures(self, loop):
        return [self.maybe_update_button(), self.subscribe_to_pins(self.pi, self.hub)]
