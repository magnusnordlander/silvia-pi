import asyncio
from utils import topics, PubSub
from PIL import Image, ImageDraw, ImageFont
from time import time

class DisplayController:
    def __init__(self, hub):
        self.hub = hub
        self.avgtemp = 0.0
        self.settemp = 0.0
        self.last_brew_time = None
        self.brew_start = None
        self.he_on = False
        self.scale_weight = None
        self.scale_is_connected = False
        self.brew_to_weight = False
        self.target_weight = None
        self.use_preinfusion = False
        self.preinfusion_time = 1.2
        self.dwell_time = 2.5
        self.avgpid = None

    async def update_ivar(self, topic, key):
        with PubSub.Subscription(self.hub, topic) as queue:
            while True:
                setattr(self, key, await queue.get())

    async def update_ivars(self):
        map = {
            'avgtemp': topics.TOPIC_AVERAGE_TEMPERATURE,
        }
        updaters = []

        for key in map:
            updaters.append(self.update_ivar(map[key], key))

        await asyncio.gather(*updaters)

    def run(self):
        lasttime = time()
        i = 0

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

        while True:  # Loops 10x/second
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
            draw.text((x, top + 40), "PID: {}".format(self.avgpid), font=font, fill=255)
            # if self.state['ignore_buttons']:
            #     draw.text((x, top + 48), "Buttons ignored", font=font, fill=255)

            self.display.draw(image)

            sleeptime = lasttime + self.sample_time - time()
            if sleeptime < 0:
                sleeptime = 0
            sleep(sleeptime)
            i += 1
            lasttime = time()


    def futures(self):
        return [self.update_ivars()]