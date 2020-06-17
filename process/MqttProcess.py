from multiprocessing import Process
import paho.mqtt.client as mqtt
from time import sleep, time

def get_shot_time(state):
    if state['last_brew_time'] is not None:
        return round(state['last_brew_time'], 2)
    elif state['brew_start'] is not None:
        return round(time() - state['brew_start'])
    else:
        return 0

writable_state = {
    "settemp": "float",
    "is_awake": "bool",
    "steam_mode": "bool",
    "brewing": "bool",
    "hot_water": "bool",
    "ignore_buttons": "bool",
    "use_preinfusion": "bool",
    "use_pump_tunings": "bool",
    "tunings": "string",
    "dynamic_kp": "float",
    "dynamic_ki": "float",
    "dynamic_kd": "float",
    "dynamic_responsiveness": "int",
    "keep_scale_connected": "bool",
    "target_weight": "float",
    "brew_to_weight": "bool",
    "preinfusion_time": "float",
    "dwell_time": "float",
}

readonly_state = {
    'avgtemp': True,
    'scale_weight': True,
    'shot_time': lambda state: get_shot_time(state)
}

class MqttSubscribeProcess(Process):
    def __init__(self, state, server, port=1883, prefix="silvia"):
        super(MqttSubscribeProcess, self).__init__()
        self.state = state
        self.server = server
        self.port = port
        self.prefix = prefix

    def run(self):
        state = self.state

        def on_connect(client, userdata, flags, rc):
            print("Connected with result code "+str(rc))

            # Subscribing in on_connect() means that if we lose the connection and
            # reconnect then subscriptions will be renewed.
            client.subscribe(list(map(lambda key: ("{}/{}/set".format(self.prefix, key), 0), writable_state.keys())))

        # The callback for when a PUBLISH message is received from the server.
        def on_message(client, userdata, msg):
            print(msg.topic+" "+str(msg.payload))
            for key in writable_state:
                if writable_state[key] == 'float':
                    self.listen_for_float_change(client, key, msg)
                elif writable_state[key] == 'bool':
                    self.listen_for_bool_change(client, key, msg)
                elif writable_state[key] == 'string':
                    self.listen_for_string_change(client, key, msg)
                elif writable_state[key] == 'int':
                    self.listen_for_int_change(client, key, msg)

        client = mqtt.Client()
        client.on_connect = on_connect
        client.on_message = on_message

        client.connect(self.server, self.port, 60)

        # Blocking call that processes network traffic, dispatches callbacks and
        # handles reconnecting.
        # Other loop*() functions are available that give a threaded interface and a
        # manual interface.
        client.loop_forever()

    def listen_for_float_change(self, client, key, msg):
        if msg.topic == self.prefix + "/" + key + "/set":
            self.state[key] = float(msg.payload)
            client.publish(self.prefix + "/" + key, self.state[key])

    def listen_for_int_change(self, client, key, msg):
        if msg.topic == self.prefix + "/" + key + "/set":
            self.state[key] = int(msg.payload)
            client.publish(self.prefix + "/" + key, self.state[key])

    def listen_for_string_change(self, client, key, msg):
        if msg.topic == self.prefix + "/" + key + "/set":
            self.state[key] = msg.payload.decode("utf-8")
            client.publish(self.prefix + "/" + key, self.state[key])

    def listen_for_bool_change(self, client, key, msg):
        if msg.topic == self.prefix + "/" + key + "/set":
            self.state[key] = msg.payload == b'True'
            client.publish(self.prefix + "/" + key, self.state[key])


class MqttPublishProcess(Process):
    def __init__(self, state, server, port=1883, prefix="silvia"):
        super(MqttPublishProcess, self).__init__()
        self.state = state
        self.server = server
        self.port = port
        self.prefix = prefix

        keys = list(writable_state.keys()) + list(readonly_state.keys())
        self.prev = {k: None for k in keys}

    def run(self):
        state = self.state

        def on_connect(client, userdata, flags, rc):
            print("Connected with result code "+str(rc))

        client = mqtt.Client()
        client.on_connect = on_connect

        sleep(3)

        client.connect(self.server, self.port, 60)

        i = 0

        while True:
            if i % 300 == 0:
                for key in writable_state:
                    self.publish_regardless(client, key)

                for key in readonly_state:
                    if callable(readonly_state[key]):
                        value = readonly_state[key](self.state)
                        client.publish(self.prefix + "/" + key, value)
                        self.prev[key] = value
                    else:
                        self.publish_regardless(client, key)
            else:
                for key in writable_state:
                    self.publish(client, key)

                for key in readonly_state:
                    if callable(readonly_state[key]):
                        value = readonly_state[key](self.state)
                        if value != self.prev[key]:
                            client.publish(self.prefix + "/" + key, value)
                            self.prev[key] = value
                    else:
                        self.publish(client, key)

            i += 1
            sleep(1)

    def publish(self, client, key):
        if key in self.state:
            if self.state[key] != self.prev[key]:
                client.publish(self.prefix + "/" + key, self.state[key])
                self.prev[key] = self.state[key]
        else:
            client.publish(self.prefix + "/" + key, "N/A")

    def publish_regardless(self, client, key):
        if key in self.state:
            client.publish(self.prefix + "/" + key, self.state[key])
            self.prev[key] = self.state[key]
        else:
            client.publish(self.prefix + "/" + key, "N/A")