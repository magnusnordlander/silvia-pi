import asyncio
import apigpio_fork
import operator

CE = 8
SCLK = 11
MOSI = 10
MISO = 9
DC = 12
RES = 22

# Constants
SSD1306_I2C_ADDRESS = 0x3C    # 011110+SA0+RW - 0x3C or 0x3D
SSD1306_SETCONTRAST = 0x81
SSD1306_DISPLAYALLON_RESUME = 0xA4
SSD1306_DISPLAYALLON = 0xA5
SSD1306_NORMALDISPLAY = 0xA6
SSD1306_INVERTDISPLAY = 0xA7
SSD1306_DISPLAYOFF = 0xAE
SSD1306_DISPLAYON = 0xAF
SSD1306_SETDISPLAYOFFSET = 0xD3
SSD1306_SETCOMPINS = 0xDA
SSD1306_SETVCOMDETECT = 0xDB
SSD1306_SETDISPLAYCLOCKDIV = 0xD5
SSD1306_SETPRECHARGE = 0xD9
SSD1306_SETMULTIPLEX = 0xA8
SSD1306_SETLOWCOLUMN = 0x00
SSD1306_SETHIGHCOLUMN = 0x10
SSD1306_SETSTARTLINE = 0x40
SSD1306_MEMORYMODE = 0x20
SSD1306_COLUMNADDR = 0x21
SSD1306_PAGEADDR = 0x22
SSD1306_COMSCANINC = 0xC0
SSD1306_COMSCANDEC = 0xC8
SSD1306_SEGREMAP = 0xA0
SSD1306_CHARGEPUMP = 0x8D
SSD1306_EXTERNALVCC = 0x1
SSD1306_SWITCHCAPVCC = 0x2

# Scrolling constants
SSD1306_ACTIVATE_SCROLL = 0x2F
SSD1306_DEACTIVATE_SCROLL = 0x2E
SSD1306_SET_VERTICAL_SCROLL_AREA = 0xA3
SSD1306_RIGHT_HORIZONTAL_SCROLL = 0x26
SSD1306_LEFT_HORIZONTAL_SCROLL = 0x27
SSD1306_VERTICAL_AND_RIGHT_HORIZONTAL_SCROLL = 0x29
SSD1306_VERTICAL_AND_LEFT_HORIZONTAL_SCROLL = 0x2A


async def start_blink(pi, address):
    await pi.connect(address)

    try:
        await pi.bb_spi_open(CE, MISO, MOSI, SCLK, 250000, 0)
    except apigpio_fork.apigpio.ApigpioError:
        pass

    await begin(pi)

    await clear(pi)

    await pi.bb_spi_close(CE)


async def begin(pi, vccstate=SSD1306_SWITCHCAPVCC):
    """Initialize display."""
    # Reset and initialize display.
    await reset(pi)
    await initialize(pi, vccstate=vccstate)
    # Turn on the display.
    await command_bytes(pi, SSD1306_DISPLAYON)


async def initialize(pi, vccstate):
    # 128x64 pixel specific initialization.
    await command_bytes(pi, SSD1306_DISPLAYOFF)  # 0xAE
    await command_bytes(pi, SSD1306_SETDISPLAYCLOCKDIV)  # 0xD5
    await command_bytes(pi, 0x80)  # the suggested ratio 0x80
    await command_bytes(pi, SSD1306_SETMULTIPLEX)  # 0xA8
    await command_bytes(pi, 0x3F)
    await command_bytes(pi, SSD1306_SETDISPLAYOFFSET)  # 0xD3
    await command_bytes(pi, 0x0)  # no offset
    await command_bytes(pi, SSD1306_SETSTARTLINE | 0x0)  # line #0
    await command_bytes(pi, SSD1306_CHARGEPUMP)  # 0x8D
    if vccstate == SSD1306_EXTERNALVCC:
        await command_bytes(pi, 0x10)
    else:
        await command_bytes(pi, 0x14)
    await command_bytes(pi, SSD1306_MEMORYMODE)  # 0x20
    await command_bytes(pi, 0x00)  # 0x0 act like ks0108
    await command_bytes(pi, SSD1306_SEGREMAP | 0x1)
    await command_bytes(pi, SSD1306_COMSCANDEC)
    await command_bytes(pi, SSD1306_SETCOMPINS)  # 0xDA
    await command_bytes(pi, 0x12)
    await command_bytes(pi, SSD1306_SETCONTRAST)  # 0x81
    if vccstate == SSD1306_EXTERNALVCC:
        await command_bytes(pi, 0x9F)
    else:
        await command_bytes(pi, 0xCF)
    await command_bytes(pi, SSD1306_SETPRECHARGE)  # 0xd9
    if vccstate == SSD1306_EXTERNALVCC:
        await command_bytes(pi, 0x22)
    else:
        await command_bytes(pi, 0xF1)
    await command_bytes(pi, SSD1306_SETVCOMDETECT)  # 0xDB
    await command_bytes(pi, 0x40)
    await command_bytes(pi, SSD1306_DISPLAYALLON_RESUME)  # 0xA4
    await command_bytes(pi, SSD1306_NORMALDISPLAY)  # 0xA6


async def reset(pi):
    # Set reset high for a millisecond.
    await pi.write(RES, 1)
    await asyncio.sleep(0.001)
    # Set reset low for 10 milliseconds.
    await pi.write(RES, 0)
    await asyncio.sleep(0.010)
    # Set reset high again.
    await pi.write(RES, 1)


async def command_bytes(pi, bytes):
    if type(bytes) == int:
        bytes = [bytes]

    await pi.write(DC, 0)
    await pi.bb_spi_xfer(CE, bytes)


async def display_bytes(pi, bytes):
    await pi.write(DC, 1)
    await pi.bb_spi_xfer(CE, bytes)


async def clear(pi):
    await command_bytes(pi, [
        SSD1306_COLUMNADDR, 0, 127,
        SSD1306_PAGEADDR, 0, 7,
    ])

    await display_bytes(pi, [0x00]*128*8)

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    pi = apigpio_fork.Pi(loop)
    address = ('192.168.10.108', 8888)
    loop.run_until_complete(start_blink(pi, address))