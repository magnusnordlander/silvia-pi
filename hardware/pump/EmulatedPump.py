class EmulatedPump(object):
    """
    Fake pump that just logs
    """

    def __init__(self):
        pass

    def __del__(self):
        self.cleanup()

    def start_pumping(self):
        print("Pump running")

    def stop_pumping(self):
        print("Pump stopped")

    def cleanup(self):
        print("Cleaning up")