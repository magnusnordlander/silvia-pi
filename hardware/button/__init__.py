from .EmulatedRandomButton import EmulatedRandomButton

try:
    from .GpioSwitchButton import GpioSwitchButton
except ModuleNotFoundError:
    pass