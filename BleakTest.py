import sys
import asyncio
from bleak import BleakClient

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