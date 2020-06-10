import sys
from time import sleep, time
from multiprocessing import Process
from PIL import Image, ImageDraw, ImageFont

class DisplayProcess(Process):
    def __init__(self, state, display, sample_time):
        super(DisplayProcess, self).__init__()

        self.sample_time = sample_time
        self.state = state
        self.display = display

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
            if self.state['last_brew_time'] is not None:
                shot_time = round(self.state['last_brew_time'], 2)
            elif self.state['brew_start'] is not None:
                shot_time = round(time() - self.state['brew_start'] ,2)
            else:
                shot_time = 0

            if self.state['is_awake']:
                draw.text((x, top + 0), "T: {}°C > {}°C".format(round(self.state['avgtemp'], 1), round(self.state['settemp'])), font=font, fill=255)
            else:
                draw.text((x, top + 0), "T: {}°C (> {}°C)".format(round(self.state['avgtemp'], 1), round(self.state['settemp'])), font=font, fill=255)
            draw.text((x, top + 8), "Time: {} s".format(shot_time), font=font, fill=255)
            scale_weight = round(self.state['scale_weight'] or 0, 1) if self.state['keep_scale_connected'] else "*"
            if self.state['brew_to_weight']:
                draw.text((x, top + 16), "M: {} g > {} g".format(scale_weight, round(self.state['target_weight'] or 0, 1)), font=font, fill=255)
            else:
                draw.text((x, top + 16), "M: {} g (> {} g)".format(scale_weight, round(self.state['target_weight'] or 0, 1)), font=font, fill=255)
            draw.text((x, top + 24), "PI: {}, T: {}, D: {}".format('Y' if self.state['use_preinfusion'] else 'N', round(self.state['preinfusion_time'], 1), round(self.state['dwell_time'], 1)), font=font, fill=255)
            draw.text((x, top + 32), "Tunings: {}".format(self.state['tunings'].capitalize()), font=font, fill=255)
            draw.text((x, top + 40), "PID: {}".format(self.state['avgpid']), font=font, fill=255)
            if self.state['ignore_buttons']:
                draw.text((x, top + 48), "Buttons ignored", font=font, fill=255)

            self.display.draw(image)

            sleeptime = lasttime + self.sample_time - time()
            if sleeptime < 0:
                sleeptime = 0
            sleep(sleeptime)
            i += 1
            lasttime = time()
