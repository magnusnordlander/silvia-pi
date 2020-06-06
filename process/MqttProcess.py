from multiprocessing import Process
import paho.mqtt.client as mqtt
from time import sleep


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
            client.subscribe([
                (self.prefix + "/settemp/set", 0),
                (self.prefix + "/is_awake/set", 0),
                (self.prefix + "/steam_mode/set", 0),
                (self.prefix + "/brewing/set", 0),
                (self.prefix + "/ignore_buttons/set", 0)
            ])

        # The callback for when a PUBLISH message is received from the server.
        def on_message(client, userdata, msg):
            print(msg.topic+" "+str(msg.payload))
            self.listen_for_float_change(client, 'settemp', msg)
            self.listen_for_bool_change(client, 'is_awake', msg)
            self.listen_for_bool_change(client, 'steam_mode', msg)
            self.listen_for_bool_change(client, 'brewing', msg)
            self.listen_for_bool_change(client, 'ignore_buttons', msg)

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

        self.prev = {
            'avgtemp': None,
            'settemp': None,
            'steam_mode': None,
            'brewing': None,
            'ignore_buttons': None,
            'is_awake': None,
        }

    def run(self):
        state = self.state

        def on_connect(client, userdata, flags, rc):
            print("Connected with result code "+str(rc))

        client = mqtt.Client()
        client.on_connect = on_connect

        client.connect(self.server, self.port, 60)

        i = 0

        while True:
            if i % 60 == 0 or (self.state['is_awake'] and i % 5 == 0):
                self.publish(client, 'avgtemp')
            self.publish(client, 'settemp')
            self.publish(client, 'steam_mode')
            self.publish(client, 'brewing')
            self.publish(client, 'ignore_buttons')
            self.publish(client, 'is_awake')

            i += 1
            sleep(1)

    def publish(self, client, key):
        if key in self.state:
            if self.state[key] != self.prev[key]:
                client.publish(self.prefix + "/" + key, self.state[key])
                self.prev[key] = self.state[key]
        else:
            client.publish(self.prefix + "/" + key, "N/A")
