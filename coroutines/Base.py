from utils import PubSub, topics
import asyncio


class Base:
    def __init__(self, hub):
        self.hub = hub
        self._ivar_map = {}
        self._authoritative = set()

    def __getattr__(self, item):
        pass

    def define_ivar(self, key, topic, default=None, authoritative=False):
        setattr(self, key, default)
        self._ivar_map[key] = topic
        if authoritative:
            self._authoritative.add(key)

    async def update_ivar(self, topic, key):
        with PubSub.Subscription(self.hub, topic) as queue:
            while True:
                setattr(self, key, await queue.get())

    async def update_ivars(self):
        updaters = []

        for key in self._ivar_map:
            updaters.append(self.update_ivar(self._ivar_map[key], key))

        await asyncio.gather(*updaters)

    def publish_authoritative(self):
        for key in self._authoritative:
            self.hub.publish(self._ivar_map[key], getattr(self, key))

    def pre_futures(self):
        return []

    def futures(self, loop):
        return [self.update_ivars()]