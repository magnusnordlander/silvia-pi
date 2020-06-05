from .EmulatedSensor import EmulatedSensor

try:
    from .Max31865Sensor import Max31865Sensor
except NotImplementedError:
    pass
