import asyncio
from utils import topics, ResizableRingBuffer, PubSub


class WeightedShotController:
    def __init__(self, hub):
        self.hub = hub
        self.current_weight = None
        self.brewing = False

        self.enable_weighted_shots = False
        self.target_weight = 0.0
        self.weighted_shot_reaction_compensation = -2
        self.tare_weight = 0.0

    async def on_start_brew(self):
        with PubSub.Subscription(self.hub, topics.TOPIC_START_BREW) as queue:
            while True:
                await queue.get()
                self.tare_weight = self.current_weight
                self.brewing = True

    async def on_stop_brew(self):
        with PubSub.Subscription(self.hub, topics.TOPIC_STOP_BREW) as queue:
            while True:
                await queue.get()
                self.tare_weight = 0.0
                self.brewing = False

    async def weight_update(self):
        with PubSub.Subscription(self.hub, topics.TOPIC_SCALE_WEIGHT) as queue:
            while True:
                weight = await queue.get()
                self.current_weight = weight

                if self.brewing and self.enable_weighted_shots:
                    nominal_weight = weight - self.weighted_shot_reaction_compensation - self.tare_weight
                    if nominal_weight >= self.target_weight:
                        self.hub.publish(topics.TOPIC_STOP_BREW, None)

    async def update_target_weight(self):
        with PubSub.Subscription(self.hub, topics.TOPIC_TARGET_WEIGHT) as queue:
            while True:
                self.target_weight = await queue.get()

    async def update_enable_weighted_shot(self):
        with PubSub.Subscription(self.hub, topics.TOPIC_ENABLE_WEIGHTED_SHOT) as queue:
            while True:
                self.enable_weighted_shots = await queue.get()

    def futures(self):
        return [
            self.on_start_brew(),
            self.on_stop_brew(),
            self.weight_update(),
            self.update_target_weight(),
            self.update_enable_weighted_shot(),
        ]
