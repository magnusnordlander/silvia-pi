import asyncio
from utils import topics, PubSub
from PIL import Image, ImageDraw, ImageFont
from time import time
from coroutines import Base


class DisplayController(Base):
    def __init__(self, hub, display):
        super().__init__(hub)
        self.display = display

        self.define_ivar('avgtemp', topics.TOPIC_AVERAGE_TEMPERATURE, 0.0)
        self.define_ivar('settemp', topics.TOPIC_SET_POINT, 0.0)
        self.define_ivar('last_brew_time', topics.TOPIC_LAST_BREW_DURATION)
        self.define_ivar('brew_start', topics.TOPIC_CURRENT_BREW_START_TIME)
        self.define_ivar('he_on', topics.TOPIC_HE_ON, False)
        self.define_ivar('scale_weight', topics.TOPIC_SCALE_WEIGHT)
        self.define_ivar('scale_is_connected', topics.TOPIC_SCALE_CONNECTED, False)
        self.define_ivar('brew_to_weight', topics.TOPIC_ENABLE_WEIGHTED_SHOT, False)
        self.define_ivar('target_weight', topics.TOPIC_TARGET_WEIGHT)
        self.define_ivar('use_preinfusion', topics.TOPIC_USE_PREINFUSION, False)
        self.define_ivar('preinfusion_time', topics.TOPIC_PREINFUSION_TIME, 1.2)
        self.define_ivar('dwell_time', topics.TOPIC_DWELL_TIME, 2.5)
        self.define_ivar('avgpid', topics.TOPIC_PID_AVERAGE_VALUE)

    async def run(self):
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
            # Draw a black filled box to clear the image.
            draw.rectangle((0, 0, width, height), outline=0, fill=0)

            # Write four lines of text.
            if self.last_brew_time is not None:
                shot_time = round(self.last_brew_time, 2)
            elif self.brew_start is not None:
                shot_time = round(time() - self.brew_start, 2)
            else:
                shot_time = 0

            if self.he_on:
                draw.text((x, top + 0), "T: {}°C > {}°C".format(round(self.avgtemp, 1), round(self.settemp)), font=font, fill=255)
            else:
                draw.text((x, top + 0), "T: {}°C (> {}°C)".format(round(self.avgtemp, 1), round(self.settemp)), font=font, fill=255)
            draw.text((x, top + 8), "Time: {} s".format(shot_time), font=font, fill=255)
            scale_weight = round(self.scale_weight or 0, 1) if self.scale_is_connected else "*"
            if self.brew_to_weight:
                draw.text((x, top + 16), "M: {} g > {} g".format(scale_weight, round(self.target_weight or 0, 1)), font=font, fill=255)
            else:
                draw.text((x, top + 16), "M: {} g (> {} g)".format(scale_weight, round(self.target_weight or 0, 1)), font=font, fill=255)
            draw.text((x, top + 24), "PI: {}, T: {}, D: {}".format('Y' if self.use_preinfusion else 'N', round(self.preinfusion_time, 1), round(self.dwell_time, 1)), font=font, fill=255)
            # draw.text((x, top + 32), "Tunings: {}".format(self.state['tunings'].capitalize()), font=font, fill=255)
            draw.text((x, top + 40), "PID: {}".format(round(self.avgpid) if self.avgpid else None), font=font, fill=255)
            # if self.state['ignore_buttons']:
            #     draw.text((x, top + 48), "Buttons ignored", font=font, fill=255)

            self.display.draw(image)

            await asyncio.sleep(1)

    def futures(self, loop):
        return [*super(DisplayController, self).futures(loop), self.run()]
