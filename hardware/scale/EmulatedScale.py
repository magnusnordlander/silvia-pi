import random

class EmulatedScale:
    def __init__(self):
        self._weight = 0.
        self._connected = False

    def connect(self):
        self._connected = True

    def disconnect(self):
        self._connected = False

    def is_connected(self):
        return self._connected

    def tare(self):
        self._weight = 0

    def weight(self):
        if not self._connected:
            return None

        self._weight += random.randint(1, 10) / 1000

        if self._weight > 200:
            self.tare()

        return self._weight