import asyncio
from utils import topics, ResizableRingBuffer
from coroutines import Base


class TemperatureSensor(Base):
    def __init__(self, hub, sensor, update_interval=0.25):
        super().__init__(hub)
        self.update_interval = update_interval
        self.sensor = sensor
        self.hub = hub
        self.ring_buffer = ResizableRingBuffer(3)

    async def update_temperature(self):
        while True:
            # Nominally takes 0.150 s
            temp_boiler, temp_group = await self.sensor.get_temp_c()
            self.ring_buffer.append(temp_boiler)
            self.hub.publish(topics.TOPIC_CURRENT_BOILER_TEMPERATURE, temp_boiler)
            self.hub.publish(topics.TOPIC_AVERAGE_BOILER_TEMPERATURE, self.ring_buffer.avg())
            self.hub.publish(topics.TOPIC_CURRENT_GROUP_TEMPERATURE, temp_group)
            self.hub.publish(topics.TOPIC_ALL_TEMPERATURES, (temp_boiler, temp_group))

            update_delay = self.sensor.get_update_delay()
            if update_delay > self.update_interval:
                raise ArithmeticError("You need a slower update interval, your sensor takes {} s".format(update_delay))

            await asyncio.sleep(self.update_interval - update_delay)

    def futures(self, loop):
        return [self.update_temperature()]
