import functools


def Debounce(threshold=100):
    """
    Simple debouncing decorator for apigpio callbacks.

    Example:

    `@Debouncer()
     def my_cb(gpio, level, tick)
         print('gpio cb: {} {} {}'.format(gpio, level, tick))
    `

    The threshold can be given to the decorator as an argument (in millisec).
    This decorator can be used both on function and object's methods.

    Warning: as the debouncer uses the tick from pigpio, which wraps around
    after approximately 1 hour 12 minutes, you could theoretically miss one
    call if your callback is called twice with that interval.
    """
    threshold *= 1000
    max_tick = 0xFFFFFFFF

    class _decorated(object):

        def __init__(self, pigpio_cb):
            self._fn = pigpio_cb
            self.last = 0
            self.is_method = False

        def __call__(self, *args, **kwargs):
            if self.is_method:
                tick = args[3]
            else:
                tick = args[2]
            if self.last > tick:
                delay = max_tick-self.last + tick
            else:
                delay = tick - self.last
            if delay > threshold:
                self._fn(*args, **kwargs)
#                print('call passed by debouncer {} {} {}'
#                      .format(tick, self.last, threshold))
                self.last = tick
            else:
                pass
#                print('call filtered out by debouncer {} {} {}'
#                      .format(tick, self.last, threshold))

        def __get__(self, instance, type=None):
            # with is called when an instance of `_decorated` is used as a class
            # attribute, which is the case when decorating a method in a class
            self.is_method = True
            return functools.partial(self, instance)

    return _decorated
