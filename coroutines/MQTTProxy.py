import asyncio
from utils import topics, ResizableRingBuffer, PubSub
from asyncio_mqtt import Client, MqttError
from contextlib import AsyncExitStack, asynccontextmanager
import time

class MQTTProxy:
    def __init__(self, hub, server, prefix="fakesilvia/", debug_mappings=False):
        self.hub = hub
        self.prefix = prefix

        self.client = Client(server)
        self.last_send = {}

        self.mappings = {
            topics.TOPIC_AVERAGE_TEMPERATURE: Mapping('avgtemp', formatter=Mapping.FloatFormatter, throttle=3),
            topics.TOPIC_PID_AVERAGE_VALUE: Mapping('avgpid', formatter=Mapping.FloatFormatter, throttle=3),
            topics.TOPIC_SCALE_WEIGHT: Mapping('scale_weight', formatter=Mapping.FloatFormatter, throttle=1),
            topics.TOPIC_SCALE_CONNECTED: Mapping('scale_is_connected'),
            topics.TOPIC_CURRENT_BREW_TIME_UPDATE: Mapping('current_brew_time', formatter=Mapping.FloatFormatter),
            topics.TOPIC_LAST_BREW_DURATION: Mapping('shot_time', formatter=Mapping.FloatFormatter),
            topics.TOPIC_STEAM_MODE: Mapping('steam_mode', mode=Mapping.MODE_READWRITE),
            topics.TOPIC_CONNECT_TO_SCALE: Mapping('keep_scale_connected', mode=Mapping.MODE_READWRITE),
            topics.TOPIC_ENABLE_WEIGHTED_SHOT: Mapping('brew_to_weight', mode=Mapping.MODE_READWRITE),
            topics.TOPIC_TARGET_WEIGHT: Mapping('target_weight', formatter=Mapping.FloatFormatter, mode=Mapping.MODE_READWRITE),
            topics.TOPIC_USE_PREINFUSION: Mapping('use_preinfusion', mode=Mapping.MODE_READWRITE),
            topics.TOPIC_SET_POINT: Mapping('settemp', mode=Mapping.MODE_READWRITE, formatter=Mapping.FloatFormatter),
            topics.TOPIC_HE_ENABLED: Mapping('is_awake', mode=Mapping.MODE_READWRITE),
        }

        if debug_mappings:
            self.mappings[topics.TOPIC_COFFEE_BUTTON] = Mapping("coffee_button", mode=Mapping.MODE_READWRITE)
            self.mappings[topics.TOPIC_WATER_BUTTON] = Mapping("water_button", mode=Mapping.MODE_READWRITE)
            self.mappings[topics.TOPIC_STEAM_BUTTON] = Mapping("steam_button", mode=Mapping.MODE_READWRITE)

    async def run_async(self):
        async with AsyncExitStack() as stack:
            # Keep track of the asyncio tasks that we create, so that
            # we can cancel them on exit
            tasks = set()
            stack.push_async_callback(self.cancel_tasks, tasks)

            # Connect to the MQTT broker
            await stack.enter_async_context(self.client)

            for key in self.mappings:
                mapping = self.mappings[key]
                if mapping.mode == Mapping.MODE_READONLY:
                    continue

                manager = self.client.filtered_messages(self.read_topic(mapping.key))
                messages = await stack.enter_async_context(manager)
                task = asyncio.create_task(self.read_values(messages, key, mapping))
                tasks.add(task)

                await self.client.subscribe(self.read_topic(mapping.key))

            task = asyncio.create_task(self.publish_values())
            tasks.add(task)

            await asyncio.gather(*tasks)

    async def cancel_tasks(self, tasks):
        for task in tasks:
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass

    async def read_values(self, messages, key, mapping):
        async for message in messages:
            self.hub.publish(key, mapping.formatter.from_mqtt(message.payload.decode()))

    async def publish_values(self):
        with PubSub.Listener(self.hub) as queue:
            while True:
                key, value = await queue.get()

                try:
                    mapping = self.mappings[key]
                except KeyError:
                    continue

                if mapping.mode == Mapping.MODE_WRITEONLY:
                    continue

                if mapping.throttle:
                    try:
                        last_send = self.last_send[mapping.key]
                    except KeyError:
                        last_send = None

                    if last_send + mapping.throttle > time.time():
                        continue

                await self.client.publish(self.write_topic(mapping.key), mapping.formatter.to_mqtt(value))
                self.last_send[mapping.key] = time.time()

    def write_topic(self, key):
        return "{}{}".format(self.prefix, key)

    def read_topic(self, key):
        return "{}{}/set".format(self.prefix, key)

    def futures(self):
        return [self.run_async()]


class Formatter:
    def __init__(self, to_mqtt, from_mqtt):
        self.from_mqtt = from_mqtt
        self.to_mqtt = to_mqtt


class Mapping:
    FloatFormatter = Formatter(lambda val: round(val, 2), float)
    StringFormatter = Formatter(str, str)
    IntFormatter = Formatter(int, int)
    BoolFormatter = Formatter(bool, lambda val: val == "True")

    MODE_READONLY = 'readonly'
    MODE_WRITEONLY = 'writeonly'
    MODE_READWRITE = 'readwrite'

    def __init__(self, key, mode=None, formatter=None, throttle=None):
        self.throttle = throttle
        self.formatter = formatter if formatter is not None else self.BoolFormatter
        self.mode = mode if mode is not None else self.MODE_READONLY
        self.key = key
