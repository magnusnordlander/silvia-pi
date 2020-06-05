import RPi.GPIO as GPIO


class GpioBoiler(object):
  """
  Water boiler connected over Raspberry Pi GPIO
  """

  def __init__(self, control_pin):
    self.control_pin = control_pin
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(self.control_pin, GPIO.OUT)

  def __del__(self):
    self.cleanup()

  def heat_on(self):
    GPIO.output(self.control_pin, 1)

  def heat_off(self):
    GPIO.output(self.control_pin, 0)

  def cleanup(self):
    GPIO.cleanup()