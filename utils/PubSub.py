import asyncio


class Hub():
    def __init__(self):
        self.subscriptions = {}
        self.listeners = set()
        self.last_sent = {}

    def debounce_publish(self, key, message):
        try:
            last_sent = self.last_sent[key]
        except KeyError:
            self.publish(key, message)
            return

        if message != last_sent:
            self.publish(key, message)

    def publish(self, key, message):
        self.last_sent[key] = message

        try:
            subscriptions = self.subscriptions[key]
        except KeyError:
            subscriptions = set()

        for queue in subscriptions:
            queue.put_nowait(message)

        for listener in self.listeners:
            listener.put_nowait((key, message))

    def add_subscription_queue(self, key, subscription):
        if not key in self.subscriptions:
            self.subscriptions[key] = set()

        self.subscriptions[key].add(subscription)

    def add_listener_queue(self, listener):
        self.listeners.add(listener)


class Subscription():
    def __init__(self, hub, key):
        self.hub = hub
        self.key = key
        self.queue = asyncio.Queue()

    def __enter__(self):
        self.hub.add_subscription_queue(self.key, self.queue)
        return self.queue

    def __exit__(self, type, value, traceback):
        self.hub.subscriptions[self.key].remove(self.queue)


class Listener():
    def __init__(self, hub):
        self.hub = hub
        self.queue = asyncio.Queue()

    def __enter__(self):
        self.hub.add_listener_queue(self.queue)
        return self.queue

    def __exit__(self, type, value, traceback):
        self.hub.listeners.remove(self.queue)