from .EmulatedBoiler import EmulatedBoiler

try:
    from .GpioBoiler import GpioBoiler
except ModuleNotFoundError:
    pass
