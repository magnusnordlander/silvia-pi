from coroutines import Base
from utils import topics, PubSub


class WeightedShotController(Base):
    def __init__(self, hub):
        super().__init__(hub)
        self.current_weight = None
        self.brewing = False

        self.define_ivar('enable_weighted_shots', topics.TOPIC_ENABLE_WEIGHTED_SHOT, False, authoritative=True)
        self.define_ivar('target_weight', topics.TOPIC_TARGET_WEIGHT, 0.0, authoritative=True)

        self.weighted_shot_reaction_compensation = -1.5
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

    def futures(self, loop):
        return [
            *super(WeightedShotController, self).futures(loop),
            self.on_start_brew(),
            self.on_stop_brew(),
            self.weight_update(),
        ]
