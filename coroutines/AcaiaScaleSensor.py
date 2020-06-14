import asyncio
from bleak import BleakClient, BleakError
from utils import topics, PubSub
import pyacaia
import sys


class AcaiaScaleSensor:
    def __init__(self, hub, address):
        self.hub = hub

        self.keep_connected = False

        self.address = address
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
            self.hub.debounce_publish(topics.TOPIC_SCALE_WEIGHT, msg.value)
        else:
            pass

    async def update_keep_connected(self):
        with PubSub.Subscription(self.hub, topics.TOPIC_CONNECT_TO_SCALE) as queue:
            while True:
                self.keep_connected = await queue.get()

    async def run(self, loop):
        while True:
            if self.keep_connected:
                try:
                    async with BleakClient(self.address, loop=loop) as client:
                        await client.is_connected()
                        self.hub.publish(topics.TOPIC_SCALE_CONNECTED, True)

                        await client.start_notify(self.ACAIA_CHR_UUID, self.notification_handler)
                        await self.ident(client)
                        while True:
                            connected = await client.is_connected()
                            if connected and self.keep_connected:
                                await self.send_heartbeat(client)
                                self.hub.publish(topics.TOPIC_SCALE_HEARTBEAT_SENT, True)
                                await asyncio.sleep(3)
                            else:
                                break
                    self.hub.publish(topics.TOPIC_SCALE_CONNECTED, False)
                except BleakError:
                    continue
            else:
                await asyncio.sleep(1)

    def futures(self, loop):
        return [self.run(loop), self.update_keep_connected()]