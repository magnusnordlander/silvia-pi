from coroutines import Base
from utils import topics, PubSub, ResizableRingBuffer
from time import time


class WeightedShotController(Base):
    def __init__(self, hub, weighted_shot_reaction_time=0):
        super().__init__(hub)
        self.current_weight = None
        self.brewing = False

        self.define_ivar('enable_weighted_shots', topics.TOPIC_ENABLE_WEIGHTED_SHOT, False, authoritative=True)
        self.define_ivar('target_weight', topics.TOPIC_TARGET_WEIGHT, 0.0, authoritative=True)

        self.weighted_shot_reaction_time = weighted_shot_reaction_time

        self.tare_weight = 0.0

        self.previous_measurements = ResizableRingBuffer(8)
        self.previous_flow_rates = ResizableRingBuffer(5)

    async def on_start_brew(self):
        with PubSub.Subscription(self.hub, topics.TOPIC_START_BREW) as queue:
            while True:
                await queue.get()
                self.tare_weight = self.current_weight
                self.previous_flow_rates.clear()
                self.previous_measurements.clear()
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
                    self.previous_measurements.append((time(), weight))
                    self.previous_flow_rates.append(self.flow_rate())

                    reaction_compensation = self.previous_flow_rates.avg() * self.weighted_shot_reaction_time

                    if reaction_compensation < 0:
                        reaction_compensation = 0

                    # Disregard reaction compensations larger than 5 grams, something is obviously up here
                    if reaction_compensation > 5:
                        reaction_compensation = 0

                    nominal_weight = weight + reaction_compensation - self.tare_weight
                    if nominal_weight >= self.target_weight:
                        self.hub.publish(topics.TOPIC_STOP_BREW, None)

    def flow_rate(self):
        first_time, first_weight = self.previous_measurements.values()[0]
        last_time, last_weight = self.previous_measurements.values()[-1]

        time_elapsed = last_time - first_time
        weight_added = last_weight - first_weight

        if time_elapsed == 0:
            return 0

        return weight_added / time_elapsed

    def futures(self, loop):
        return [
            *super(WeightedShotController, self).futures(loop),
            self.on_start_brew(),
            self.on_stop_brew(),
            self.weight_update(),
        ]
