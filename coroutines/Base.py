from utils import PubSub, topics
import asyncio


class Base:
    def __init__(self, hub):
        self.hub = hub
        self._ivar_map = {}

    def __getattr__(self, item):
        pass

    def define_ivar(self, key, topic, default=None):
        setattr(self, key, default)
        self._ivar_map[key] = topic

    async def update_ivar(self, topic, key):
        with PubSub.Subscription(self.hub, topic) as queue:
            while True:
                setattr(self, key, await queue.get())

    async def update_ivars(self):
        updaters = []

        for key in self._ivar_map:
            updaters.append(self.update_ivar(self._ivar_map[key], key))

        await asyncio.gather(*updaters)

    def pre_futures(self):
        return []

    def futures(self):
        return [self.update_ivars()]