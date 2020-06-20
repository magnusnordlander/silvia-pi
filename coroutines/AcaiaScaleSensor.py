import asyncio
from bleak import BleakClient, BleakError
from utils import topics, PubSub
import pyacaia
from coroutines import Base

class AcaiaScaleSensor(Base):
    def __init__(self, hub, address):
        super().__init__(hub)

        self.define_ivar('keep_connected', topics.TOPIC_CONNECT_TO_SCALE, default=False, authoritative=True)

        self.was_disconnected = False
        self.scale_connected = False

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
        if len(self.packet) < 5:
            return

        msg = pyacaia.decode(self.packet)
        self.packet = None

        if not msg:
            return

        if msg.msgType == 5:
            self.hub.debounce_publish(topics.TOPIC_SCALE_WEIGHT, msg.value)
        else:
            pass

    async def run(self, loop):
        while True:
            if self.keep_connected:
                try:
                    client = BleakClient(self.address, loop=loop)
                    await client.connect()
                    self.was_disconnected = False

                    def disconnect_callback(client, future=None):
                        print("Got disconnected from scale")
                        self.was_disconnected = True

                    client.set_disconnected_callback(disconnect_callback)

                    await client.is_connected()
                    self.scale_connected = True
                    self.hub.publish(topics.TOPIC_SCALE_CONNECTED, self.scale_connected)

                    await client.start_notify(self.ACAIA_CHR_UUID, self.notification_handler)
                    await self.ident(client)
                    while True:
                        if not self.was_disconnected and self.keep_connected:
                            await self.send_heartbeat(client)
                            self.hub.publish(topics.TOPIC_SCALE_HEARTBEAT_SENT, True)
                            await asyncio.sleep(3)
                        elif not self.keep_connected:
                            await client.disconnect()
                            break
                        else:  # if self.was_disconnected
                            # for some weird reason, we *really* can't call client.disconnect in this case when using bluez
                            break

                    self.scale_connected = False
                    self.hub.publish(topics.TOPIC_SCALE_CONNECTED, self.scale_connected)
                except BleakError:
                    continue
            else:
                await asyncio.sleep(1)

    def publish_authoritative(self):
        super().publish_authoritative()
        self.hub.publish(topics.TOPIC_SCALE_CONNECTED, self.scale_connected)

    def futures(self, loop):
        return [
            *super(AcaiaScaleSensor, self).futures(loop),
            self.run(loop)
        ]