from .EmulatedPump import EmulatedPump

try:
    from .GpioPump import GpioPump
except ModuleNotFoundError:
    pass
