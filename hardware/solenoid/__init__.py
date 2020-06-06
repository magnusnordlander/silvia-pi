from .EmulatedSolenoid import EmulatedSolenoid

try:
    from .GpioSolenoid import GpioSolenoid
except ModuleNotFoundError:
    pass
