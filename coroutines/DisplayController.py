import asyncio
from utils import topics, PubSub
from PIL import Image, ImageDraw, ImageFont
from time import time
from coroutines import Base
import apigpio_fork

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


class DisplayController(Base):
    def __init__(self, hub, pi, cs_num, dev_num, dc, res):
        super().__init__(hub)
        self.res = res
        self.dc = dc
        self.dev_num = dev_num
        self.cs_num = cs_num
        self.pi = pi

        self.low_contrast = 0x00
        self.high_contrast = 0xCF

        self.define_ivar('oled_saver', topics.TOPIC_OLED_SAVER, True, authoritative=True)

        self.spi_handle = None

        self.define_ivar('avgtemp', topics.TOPIC_AVERAGE_BOILER_TEMPERATURE, 0.0)
        self.define_ivar('settemp', topics.TOPIC_SET_POINT, 0.0)
        self.define_ivar('group_temp', topics.TOPIC_CURRENT_GROUP_TEMPERATURE, 0.0)
        self.define_ivar('last_brew_time', topics.TOPIC_LAST_BREW_DURATION)
        self.define_ivar('brew_start', topics.TOPIC_CURRENT_BREW_START_TIME)
        self.define_ivar('he_enabled', topics.TOPIC_HE_ENABLED, False)
        self.define_ivar('scale_weight', topics.TOPIC_SCALE_WEIGHT)
        self.define_ivar('scale_is_connected', topics.TOPIC_SCALE_CONNECTED, False)
        self.define_ivar('keep_scale_connected', topics.TOPIC_CONNECT_TO_SCALE, False)
        self.define_ivar('brew_to_weight', topics.TOPIC_ENABLE_WEIGHTED_SHOT, False)
        self.define_ivar('target_weight', topics.TOPIC_TARGET_WEIGHT)
        self.define_ivar('dose', topics.TOPIC_DOSE, None)
        self.define_ivar('use_preinfusion', topics.TOPIC_USE_PREINFUSION, False)
        self.define_ivar('preinfusion_time', topics.TOPIC_PREINFUSION_TIME, 1.2)
        self.define_ivar('dwell_time', topics.TOPIC_DWELL_TIME, 2.5)
        self.define_ivar('avgpid', topics.TOPIC_PID_AVERAGE_VALUE)
        self.define_ivar('tunings', topics.TOPIC_PID_TUNINGS)
        self.define_ivar('responsiveness', topics.TOPIC_PID_RESPONSIVENESS)
        self.define_ivar('steam_mode', topics.TOPIC_STEAM_MODE, False)
        self.define_ivar('steam_setpoint', topics.TOPIC_STEAM_TEMPERATURE_SET_POINT)
        self.define_ivar('steam_delta', topics.TOPIC_STEAM_TEMPERATURE_DELTA)

    async def run(self):
        try:
            self.spi_handle = await self.pi.spi_open(0, 24000000, 256)
            print("Opened display SPI handle ", self.spi_handle)
        except apigpio_fork.apigpio.ApigpioError as err:
            print("Pigpio error, display disabled")
            print(err)
            return

        await self.begin()
        await self.clear()

        try:
            # Create blank image for drawing.
            # Make sure to create image with mode '1' for 1-bit color.
            width = 128
            height = 64
            image = Image.new("1", (width, height))

            # Get drawing object to draw on image.
            draw = ImageDraw.Draw(image)

            # Draw a black filled box to clear the image.
            draw.rectangle((0, 0, width, height), outline=0, fill=0)

            # Draw some shapes.
            # First define some constants to allow easy resizing of shapes.
            padding = 0
            top = padding
            bottom = height - padding
            # Move left to right keeping track of the current x position for drawing shapes.
            x = padding

            # Load default font.
            font = ImageFont.load_default()

            while True:
                if not self.oled_saver or self.he_enabled:
                    self.draw_image(draw, top, bottom, width, height, font, x)
                else:
                    self.draw_dots(draw, top, bottom, width, height, font, x)
                await self.display_image(image)

                contrast = self.high_contrast if self.he_enabled else self.low_contrast
                await self.command_bytes([SSD1306_SETCONTRAST, contrast])

                await asyncio.sleep(1)
        finally:
            await self.close_handle()

    async def close_handle(self):
        if self.spi_handle is not None:
            print("Clearing display")
            await self.clear()

            print("Closing SPI handle ", self.spi_handle)
            await self.pi.spi_close(self.spi_handle)
            self.spi_handle = None

    def draw_dots(self, draw, top, bottom, width, height, font, x):
        # Draw a black filled box to clear the image.
        draw.rectangle((0, 0, width, height), outline=0, fill=0)
        draw.point((width-1, height-1), fill=255)
        draw.point((width-3, height-1), fill=255)
        draw.point((width-5, height-1), fill=255)

    def draw_image(self, draw, top, bottom, width, height, font, x):
        # Draw a black filled box to clear the image.
        draw.rectangle((0, 0, width, height), outline=0, fill=0)

        if self.brew_start is not None:
            shot_time = round(time() - self.brew_start, 2)
        elif self.last_brew_time is not None:
            shot_time = round(self.last_brew_time, 2)
        else:
            shot_time = 0

        if self.scale_is_connected:
            scale_weight = round(self.scale_weight or 0, 1)
        else:
            scale_weight = "*" if not self.keep_scale_connected else "#"

        if self.steam_mode:
            draw.text((x, top + 0), "Steam mode", font=font, fill=255)
            if self.he_enabled:
                draw.text((x, top + 8), "T: {}°C > {}°C".format(round(self.avgtemp, 1), self.steam_setpoint), font=font,
                          fill=255)
            else:
                draw.text((x, top + 8), "T: {}°C (> {}°C)".format(round(self.avgtemp, 1), self.steam_setpoint),
                          font=font, fill=255)
            draw.text((x, top + 16), "Group T: {}°C".format(round(self.group_temp, 1)), font=font, fill=255)

            draw.text((x, top + 24), "Time: {} s".format(shot_time), font=font, fill=255)

            if self.brew_to_weight:
                draw.text((x, top + 32), "M: {} g > {} g".format(scale_weight, round(self.target_weight or 0, 1)),
                          font=font, fill=255)
            else:
                draw.text((x, top + 32), "M: {} g (> {} g)".format(scale_weight, round(self.target_weight or 0, 1)),
                          font=font, fill=255)

        else:
            if self.he_enabled:
                draw.text((x, top + 0), "T: {}°C > {}°C".format(round(self.avgtemp, 1), round(self.settemp)), font=font,
                          fill=255)
            else:
                draw.text((x, top + 0), "T: {}°C (> {}°C)".format(round(self.avgtemp, 1), round(self.settemp)),
                          font=font, fill=255)
            draw.text((x, top + 8), "Group T: {}°C".format(round(self.group_temp, 1)), font=font, fill=255)
            draw.text((x, top + 16), "Time: {} s".format(shot_time), font=font, fill=255)

            if self.brew_to_weight:
                draw.text((x, top + 24), "M: {} g > {} g".format(scale_weight, round(self.target_weight or 0, 1)),
                          font=font, fill=255)
            else:
                draw.text((x, top + 24), "M: {} g (> {} g)".format(scale_weight, round(self.target_weight or 0, 1)),
                          font=font, fill=255)
            dose = str(round(self.dose, 1)) + "g" if self.dose is not None else "N/A"
            draw.text((x, top + 32), "Dose: {}".format(dose), font=font, fill=255)

            draw.text((x, top + 40), "PI: {}, T: {}, D: {}".format('Y' if self.use_preinfusion else 'N',
                                                                   round(self.preinfusion_time, 1),
                                                                   round(self.dwell_time, 1)), font=font, fill=255)
            if self.tunings:
                draw.text((x, top + 48), "K: ({:.1f},{:.1f},{:.1f},{})".format(*self.tunings, self.responsiveness),
                          font=font, fill=255)
            draw.text((x, top + 56), "PID: {}".format(round(self.avgpid) if self.avgpid else None), font=font, fill=255)

    async def display_image(self, image):
        buffer = [0]*(128*8)

        flipped = image.transpose(Image.ROTATE_180)

        # Grab all the pixels from the image, faster than getpixel.
        pix = flipped.load()
        # Iterate through the memory pages
        index = 0
        for page in range(8):
            # Iterate through all x axis columns.
            for x in range(128):
                # Set the bits for the column of pixels at the current position.
                bits = 0
                # Don't use range here as it's a bit slow
                for bit in [0, 1, 2, 3, 4, 5, 6, 7]:
                    bits = bits << 1
                    bits |= 0 if pix[(x, page*8+7-bit)] == 0 else 1
                # Update buffer byte and increment to next byte.
                buffer[index] = bits
                index += 1

        await self.command_bytes([
            SSD1306_COLUMNADDR, 0, 127,
            SSD1306_PAGEADDR, 0, 7,
        ])

        await self.display_bytes(buffer)

    async def begin(self, vccstate=SSD1306_SWITCHCAPVCC):
        """Initialize display."""
        # Reset and initialize display.
        await self.reset()
        await self.initialize(vccstate=vccstate)
        # Turn on the display.
        await self.command_bytes(SSD1306_DISPLAYON)

    async def initialize(self, vccstate):
        # 128x64 pixel specific initialization.
        await self.command_bytes(SSD1306_DISPLAYOFF)  # 0xAE
        await self.command_bytes(SSD1306_SETDISPLAYCLOCKDIV)  # 0xD5
        await self.command_bytes(0x80)  # the suggested ratio 0x80
        await self.command_bytes(SSD1306_SETMULTIPLEX)  # 0xA8
        await self.command_bytes(0x3F)
        await self.command_bytes(SSD1306_SETDISPLAYOFFSET)  # 0xD3
        await self.command_bytes(0x0)  # no offset
        await self.command_bytes(SSD1306_SETSTARTLINE | 0x0)  # line #0
        await self.command_bytes(SSD1306_CHARGEPUMP)  # 0x8D
        if vccstate == SSD1306_EXTERNALVCC:
            await self.command_bytes(0x10)
        else:
            await self.command_bytes(0x14)
        await self.command_bytes(SSD1306_MEMORYMODE)  # 0x20
        await self.command_bytes(0x00)  # 0x0 act like ks0108
        await self.command_bytes(SSD1306_SEGREMAP | 0x1)
        await self.command_bytes(SSD1306_COMSCANDEC)
        await self.command_bytes(SSD1306_SETCOMPINS)  # 0xDA
        await self.command_bytes(0x12)
        await self.command_bytes(SSD1306_SETCONTRAST)  # 0x81
        if vccstate == SSD1306_EXTERNALVCC:
            await self.command_bytes(0x9F)
        else:
            await self.command_bytes(self.high_contrast)
        await self.command_bytes(SSD1306_SETPRECHARGE)  # 0xd9
        if vccstate == SSD1306_EXTERNALVCC:
            await self.command_bytes(0x22)
        else:
            await self.command_bytes(0xF1)
        await self.command_bytes(SSD1306_SETVCOMDETECT)  # 0xDB
        await self.command_bytes(0x40)
        await self.command_bytes(SSD1306_DISPLAYALLON_RESUME)  # 0xA4
        await self.command_bytes(SSD1306_NORMALDISPLAY)  # 0xA6

    async def reset(self):
        # Set reset high for a millisecond.
        await self.pi.write(self.res, 1)
        await asyncio.sleep(0.001)
        # Set reset low for 10 milliseconds.
        await self.pi.write(self.res, 0)
        await asyncio.sleep(0.010)
        # Set reset high again.
        await self.pi.write(self.res, 1)

    async def command_bytes(self, bytes):
        if self.spi_handle is None:
            print("No SPI Handle, can't send command")
            return

        if type(bytes) == int:
            bytes = [bytes]

        await self.pi.write(self.dc, 0)
        await self.pi.spi_write(self.spi_handle, bytes)

    async def display_bytes(self, bytes):
        if self.spi_handle is None:
            print("No SPI Handle, can't send display data")
            return

        await self.pi.write(self.dc, 1)
        await self.pi.spi_write(self.spi_handle, bytes)

    async def clear(self):
        await self.command_bytes([
            SSD1306_COLUMNADDR, 0, 127,
            SSD1306_PAGEADDR, 0, 7,
        ])

        await self.display_bytes([0x00] * 128 * 8)

    async def invert(self):
        while True:
            await asyncio.sleep(60*60*8)
            await self.command_bytes(SSD1306_INVERTDISPLAY)
            await asyncio.sleep(1)
            await self.command_bytes(SSD1306_NORMALDISPLAY)

    def futures(self, loop):
        return [*super(DisplayController, self).futures(loop), self.run(), self.invert()]
