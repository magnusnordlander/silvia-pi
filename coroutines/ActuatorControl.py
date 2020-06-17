import asyncio
from utils import topics, ResizableRingBuffer, PubSub


class ActuatorControl:
    def __init__(self, hub, pump, solenoid):
        self.solenoid = solenoid
        self.pump = pump
        self.hub = hub

    async def update_pump(self):
        with PubSub.Subscription(self.hub, topics.TOPIC_PUMP_ON) as queue:
            while True:
                if await queue.get():
                    self.pump.start_pumping()
                else:
                    self.pump.stop_pumping()

    async def update_solenoid(self):
        with PubSub.Subscription(self.hub, topics.TOPIC_SOLENOID_OPEN) as queue:
            while True:
                if await queue.get():
                    self.solenoid.open()
                else:
                    self.solenoid.close()

    def futures(self):
        return [self.update_pump(), self.update_solenoid()]
