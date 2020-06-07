import asyncio
from bleak import BleakClient
from utils import topics
import pyacaia
import sys

class AcaiaScaleSensor:
    def __init__(self, hub):
        self.hub = hub
        self.address = "9B0F0A71-568C-4DB5-9002-F1D09B240D0A" if sys.platform == "darwin" else "00:1c:97:1a:a0:2f"
        self.ACAIA_CHR_UUID = "00002a80-0000-1000-8000-00805f9b34fb"
        self.MAGIC1 = 0xef
        self.MAGIC2 = 0xdd

        self.i_ = 0
        self.packet = []

    async def ident(self, client):
        await client.write_gatt_char(self.ACAIA_CHR_UUID, pyacaia.encodeId())
        await client.write_gatt_char(self.ACAIA_CHR_UUID, pyacaia.encodeNotificationRequest())

    async def send_heartbeat(self, client):
        await client.write_gatt_char(self.ACAIA_CHR_UUID, pyacaia.encodeHeartbeat())

    def add_buffer(self, buffer2):
        packet_len = 0

        if self.packet:
            packet_len = len(self.packet)

        result = bytearray(packet_len + len(buffer2))

        for i in range(packet_len):
            self.i_ = self.packet[i]
            result[i] = self.i_

        for i in range(len(buffer2)):
            result[i + packet_len] = buffer2[i]

        self.packet = result

    def notification_handler(self, sender, data):
        self.add_buffer(data)
        if len(self.packet) <= 3:
            return

        msg = pyacaia.decode(self.packet)
        self.packet = None

        if not msg:
            return

        if msg.msgType == 5:
            self.hub.publish(topics.TOPIC_SCALE_WEIGHT, msg.value)
        else:
            pass

    async def run(self, loop):
        async with BleakClient(self.address, loop=loop) as client:
            x = await client.is_connected()
            self.hub.publish(topics.TOPIC_SCALE_CONNECTED, True)

            await client.start_notify(self.ACAIA_CHR_UUID, self.notification_handler)
            await self.ident(client)
            i = 0
            while i < 10:
                i += 1
                await self.send_heartbeat(client)
                self.hub.publish(topics.TOPIC_SCALE_HEARTBEAT_SENT, True)
                await asyncio.sleep(5)

            await client.disconnect()
            self.hub.publish(topics.TOPIC_SCALE_CONNECTED, False)

    def futures(self, loop):
        return [self.run(loop)]