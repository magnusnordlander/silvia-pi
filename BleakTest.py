import sys
import asyncio
import logging
from bleak import BleakClient

logging.root.setLevel(logging.DEBUG)
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.DEBUG)
FORMAT = "%(asctime)-15s %(name)-8s %(levelname)s: %(message)s"
handler.setFormatter(logging.Formatter(fmt=FORMAT))
logging.root.addHandler(handler)

async def run(loop):
    print("Running")
    async with BleakClient("9B0F0A71-568C-4DB5-9002-F1D09B240D0A" if sys.platform == "darwin" else "00:1c:97:1a:a0:2f", loop=loop) as client:
        print("Created")
        await client.is_connected()
        print("Connected")
        await asyncio.sleep(3)
        await client.disconnect()
        print("Disconnected")
    print("Done")

loop = asyncio.get_event_loop()
loop.run_until_complete(run(loop))
loop.run_forever()