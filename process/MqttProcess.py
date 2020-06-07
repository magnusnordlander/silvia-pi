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
                (self.prefix + "/hot_water/set", 0),
                (self.prefix + "/ignore_buttons/set", 0),
                (self.prefix + "/use_preinfusion/set", 0),
                (self.prefix + "/use_pump_tunings/set", 0),
                (self.prefix + "/tunings/set", 0),
                (self.prefix + "/dynamic_kp/set", 0),
                (self.prefix + "/dynamic_ki/set", 0),
                (self.prefix + "/dynamic_kd/set", 0),
                (self.prefix + "/dynamic_responsiveness/set", 0),
            ])

        # The callback for when a PUBLISH message is received from the server.
        def on_message(client, userdata, msg):
            print(msg.topic+" "+str(msg.payload))
            self.listen_for_float_change(client, 'settemp', msg)
            self.listen_for_bool_change(client, 'is_awake', msg)
            self.listen_for_bool_change(client, 'steam_mode', msg)
            self.listen_for_bool_change(client, 'brewing', msg)
            self.listen_for_bool_change(client, 'hot_water', msg)
            self.listen_for_bool_change(client, 'ignore_buttons', msg)
            self.listen_for_bool_change(client, 'use_preinfusion', msg)
            self.listen_for_bool_change(client, 'use_pump_tunings', msg)
            self.listen_for_string_change(client, 'tunings', msg)
            self.listen_for_float_change(client, 'dynamic_kp', msg)
            self.listen_for_float_change(client, 'dynamic_ki', msg)
            self.listen_for_float_change(client, 'dynamic_kd', msg)
            self.listen_for_int_change(client, 'dynamic_responsiveness', msg)

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

        self.prev = {
            'avgtemp': None,
            'settemp': None,
            'steam_mode': None,
            'brewing': None,
            'hot_water': None,
            'ignore_buttons': None,
            'is_awake': None,
            'use_pump_tunings': None,
            'use_preinfusion': None,
            'tunings': None,
            'dynamic_kp': None,
            'dynamic_ki': None,
            'dynamic_kd': None,
            'dynamic_responsiveness': None,
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
            if i % 300 == 0:
                self.publish_regardless(client, 'avgtemp')
                self.publish_regardless(client, 'settemp')
                self.publish_regardless(client, 'steam_mode')
                self.publish_regardless(client, 'brewing')
                self.publish_regardless(client, 'hot_water')
                self.publish_regardless(client, 'ignore_buttons')
                self.publish_regardless(client, 'is_awake')
                self.publish_regardless(client, 'use_preinfusion')
                self.publish_regardless(client, 'use_pump_tunings')
                self.publish_regardless(client, 'tunings')
                self.publish_regardless(client, 'dynamic_kp')
                self.publish_regardless(client, 'dynamic_ki')
                self.publish_regardless(client, 'dynamic_kd')
                self.publish_regardless(client, 'dynamic_responsiveness')
            else:
                if i % 60 == 0 or (self.state['is_awake'] and i % 5 == 0):
                    self.publish(client, 'avgtemp')
                self.publish(client, 'settemp')
                self.publish(client, 'steam_mode')
                self.publish(client, 'brewing')
                self.publish(client, 'hot_water')
                self.publish(client, 'ignore_buttons')
                self.publish(client, 'is_awake')
                self.publish(client, 'use_preinfusion')
                self.publish(client, 'use_pump_tunings')
                self.publish(client, 'tunings')
                self.publish(client, 'dynamic_kp')
                self.publish(client, 'dynamic_ki')
                self.publish(client, 'dynamic_kd')
                self.publish(client, 'dynamic_responsiveness')

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