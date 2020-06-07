import asyncio
from utils import topics, ResizableRingBuffer


class TemperatureSensor:
    def __init__(self, hub, sensor, update_interval=0.25):
        self.update_interval = update_interval
        self.sensor = sensor
        self.hub = hub
        self.ring_buffer = ResizableRingBuffer(3)

    async def update_temperature(self):
        while True:
            # Nominally takes 0.075 s
            temp = await self.sensor.get_temp_c()
            self.ring_buffer.append(temp)
            self.hub.publish(topics.TOPIC_CURRENT_TEMPERATURE, temp)
            self.hub.publish(topics.TOPIC_AVERAGE_TEMPERATURE, self.ring_buffer.avg())

            update_delay = self.sensor.get_update_delay()
            if update_delay > self.update_interval:
                raise ArithmeticError("You need a slower update interval, your sensor takes {} s".format(update_delay))

            await asyncio.sleep(self.update_interval - update_delay)

    def futures(self):
        return [self.update_temperature()]
