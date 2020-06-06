class EmulatedSolenoid(object):
    """
    Fake solenoid that just logs
    """

    def __init__(self):
        pass

    def __del__(self):
        self.cleanup()

    def open(self):
        print("Solenoid open")

    def close(self):
        print("Solenoid closed")

    def cleanup(self):
        print("Cleaning up")