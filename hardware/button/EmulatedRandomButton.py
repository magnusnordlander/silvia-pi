import random


class EmulatedRandomButton:
    def __init__(self):
        self._button_state = False

    def button_state(self):
        if random.randint(0, 1000) == 0:
            self._button_state = not self._button_state

        return self._button_state
