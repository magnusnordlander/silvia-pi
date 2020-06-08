import RPi.GPIO as GPIO


class GpioPump(object):
    def __init__(self, control_pin):
        self.control_pin = control_pin
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.control_pin, GPIO.OUT)

    def __del__(self):
        self.cleanup()

    def start_pumping(self):
        print("Pump running")
        GPIO.output(self.control_pin, 1)

    def stop_pumping(self):
        print("Pump stopped")
        GPIO.output(self.control_pin, 0)

    def cleanup(self):
        print("Cleaning up GPIO pump " + str(self.control_pin))
        GPIO.cleanup()