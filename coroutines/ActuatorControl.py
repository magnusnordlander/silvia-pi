from utils import topics, PubSub
from coroutines import Base


class ActuatorControl(Base):
    def __init__(self, hub, pi, pump_pin, solenoid_pin):
        super().__init__(hub)
        self.pump_pin = pump_pin
        self.solenoid_pin = solenoid_pin
        self.pi = pi

    async def update_pump(self):
        with PubSub.Subscription(self.hub, topics.TOPIC_PUMP_ON) as queue:
            while True:
                if await queue.get():
                    print("Starting pump")
                    await self.pi.write(self.pump_pin, 1)
                else:
                    print("Stopping pump")
                    await self.pi.write(self.pump_pin, 0)

    async def update_solenoid(self):
        with PubSub.Subscription(self.hub, topics.TOPIC_SOLENOID_OPEN) as queue:
            while True:
                if await queue.get():
                    print("Opening solenoid")
                    await self.pi.write(self.solenoid_pin, 1)
                else:
                    print("Closing solenoid")
                    await self.pi.write(self.solenoid_pin, 0)

    def futures(self, loop):
        return [self.update_pump(), self.update_solenoid()]
