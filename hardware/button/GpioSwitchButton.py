import RPi.GPIO as GPIO


class GpioSwitchButton(object):
    """
    Switch (i.e. non momentary) bytton over Raspberry Pi GPIO
    """

    def __init__(self, control_pin):
        self.control_pin = control_pin
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.control_pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

    def __del__(self):
        self.cleanup()

    def button_state(self):
        return GPIO.input(self.control_pin) == GPIO.HIGH

    def cleanup(self):
        GPIO.cleanup()
