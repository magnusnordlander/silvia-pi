import RPi.GPIO as GPIO


class GpioBoiler(object):
    """
    Water boiler connected over Raspberry Pi GPIO
    """

    def __init__(self, control_pin):
        self.control_pin = control_pin
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.control_pin, GPIO.OUT)

        self.last_mode = False

    def __del__(self):
        self.cleanup()

    def heat_on(self):
        if self.last_mode == False:
            #print("Heat on")
            pass
        self.last_mode = True
        GPIO.output(self.control_pin, 1)

    def heat_off(self):
        if self.last_mode == True:
            #print("Heat off")
            pass
        self.last_mode = False
        GPIO.output(self.control_pin, 0)

    def force_heat_off(self):
        print("Heating element forced off")
        self.last_mode = False
        GPIO.output(self.control_pin, 0)

    def cleanup(self):
        print("Cleaning up GPIO boiler " + str(self.control_pin))
        GPIO.cleanup()
