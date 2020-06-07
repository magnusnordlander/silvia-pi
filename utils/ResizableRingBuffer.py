from collections import deque

class ResizableRingBuffer:
    """ class that implements a resizable ring buffer"""

    def __init__(self, size_max):
        self.size_max = size_max
        self.deque = deque(maxlen=size_max)

    def append(self, x):
        self.deque.append(x)

    def resize(self, new_size):
        self.deque = deque(self.deque, maxlen=new_size)
        self.size_max = new_size

    def avg(self):
        return sum(self.deque) / len(self.deque)