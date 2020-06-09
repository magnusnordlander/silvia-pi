from pyacaia import AcaiaScale as Acaia


class AcaiaScale:
    def __init__(self, mac, backend='pygatt'):
        self.scale = Acaia(mac=mac, backend=backend)

    def connect(self):
        self.scale.connect()

    def disconnect(self):
        self.scale.disconnect()

    def is_connected(self):
        return self.scale.connected

    def tare(self):
        self.scale.tare()

    def weight(self):
        return self.scale.weight
