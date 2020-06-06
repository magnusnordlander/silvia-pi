import RPi.GPIO as GPIO


class GpioSolenoid(object):
    """
    Solenoid connected over Raspberry Pi GPIO
    """

    def __init__(self, control_pin):
        self.control_pin = control_pin
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.control_pin, GPIO.OUT)

    def __del__(self):
        self.cleanup()

    def open(self):
        print("Solenoid open")
        GPIO.output(self.control_pin, 1)

    def close(self):
        print("Solenoid closed")
        GPIO.output(self.control_pin, 0)

    def cleanup(self):
        GPIO.cleanup()
