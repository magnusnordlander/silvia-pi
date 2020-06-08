from .EmulatedScale import EmulatedScale

try:
    from .AcaiaScale import AcaiaScale
except ModuleNotFoundError:
    pass
