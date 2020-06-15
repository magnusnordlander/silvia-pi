import asyncio
import apigpio
import config as conf
from utils import topics
from functools import partial

async def _input_forward_to_hub(gpio, level, tick, hub, topic, pi):
    # Wait 5ms then see if it's still the same
    await asyncio.sleep(0.005)
    new_level = await pi.read(gpio)
    if new_level == level:
        hub.publish(topic, level == 1)
    else:
        print("False button press on "+topic)

@apigpio.Debounce()
def on_input_forward_to_hub(gpio, level, tick, hub, topic, pi, loop):
    loop.run(_input_forward_to_hub(gpio, level, tick, hub, topic, pi))

class PigpioPins:
    def __init__(self, loop, hub):
        self.loop = loop
        self.hub = hub
        self.pi = apigpio.Pi(self.loop)

    @asyncio.coroutine
    def subscribe_to_pins(self, pi, hub):
        pins = {
            conf.brew_button_pin: topics.TOPIC_COFFEE_BUTTON,
            conf.steam_button_pin: topics.TOPIC_STEAM_BUTTON,
            conf.water_button_pin: topics.TOPIC_WATER_BUTTON,
        }

        for pin in pins:
            yield from pi.set_mode(pin, apigpio.INPUT)
            yield from pi.set_pull_up_down(pin, apigpio.PUD_DOWN)
            yield from pi.add_callback(pin, edge=apigpio.EITHER_EDGE, func=partial(on_input_forward_to_hub, hub=hub, topic=pins[pin], pi=pi, loop=self.loop))

    def pre_futures(self):
        address = ('192.168.10.107', 8888)
        return [self.pi.connect(address)]

    def futures(self):
        return [self.subscribe_to_pins(self.pi, self.hub)]
