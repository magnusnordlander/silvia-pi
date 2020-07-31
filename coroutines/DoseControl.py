from utils import topics, PubSub
from coroutines import Base


class DoseControl(Base):
    def __init__(self, hub, default_target_ratio=2.0):
        super().__init__(hub)

        self.define_ivar("target_ratio", topics.TOPIC_TARGET_RATIO, default_target_ratio, authoritative=True)
        self.define_ivar("dose", topics.TOPIC_DOSE, None, authoritative=True)
        self.define_ivar('current_weight', topics.TOPIC_SCALE_WEIGHT)

    async def capture_dose(self):
        with PubSub.Subscription(self.hub, topics.TOPIC_CAPTURE_DOSE) as queue:
            while True:
                await queue.get()
                self.hub.publish(topics.TOPIC_DOSE, self.current_weight)

    async def capture_dose_and_set_weight(self):
        with PubSub.Subscription(self.hub, topics.TOPIC_CAPTURE_DOSE_AND_SET_TARGET_WEIGHT) as queue:
            while True:
                await queue.get()
                if self.current_weight is not None:
                    self.hub.publish(topics.TOPIC_DOSE, self.current_weight)
                    self.hub.publish(topics.TOPIC_TARGET_WEIGHT, round(self.current_weight * self.target_ratio, 1))

    def futures(self, loop):
        return [
            *super(DoseControl, self).futures(loop),
            self.capture_dose(),
            self.capture_dose_and_set_weight(),
        ]