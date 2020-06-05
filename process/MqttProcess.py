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
            client.subscribe([(self.prefix+"/settemp/set", 0), (self.prefix+"/is_awake/set", 0), (self.prefix+"/steam_mode/set", 0)])

        # The callback for when a PUBLISH message is received from the server.
        def on_message(client, userdata, msg):
            print(msg.topic+" "+str(msg.payload))
            if msg.topic == self.prefix+"/settemp/set":
                state['settemp'] = float(msg.payload)
                client.publish(self.prefix+"/settemp", state['settemp'])
            elif msg.topic == self.prefix+"/is_awake/set":
                state['is_awake'] = msg.payload == b'True'
                client.publish(self.prefix+"/is_awake", state['is_awake'])
            elif msg.topic == self.prefix+"/steam_mode/set":
                state['steam_mode'] = msg.payload == b'True'
                client.publish(self.prefix+"/steam_mode", state['steam_mode'])


        client = mqtt.Client()
        client.on_connect = on_connect
        client.on_message = on_message

        client.connect(self.server, self.port, 60)

        # Blocking call that processes network traffic, dispatches callbacks and
        # handles reconnecting.
        # Other loop*() functions are available that give a threaded interface and a
        # manual interface.
        client.loop_forever()


class MqttPublishProcess(Process):
    def __init__(self, state, server, port=1883, prefix="silvia"):
        super(MqttPublishProcess, self).__init__()
        self.state = state
        self.server = server
        self.port = port
        self.prefix = prefix

    def run(self):
        state = self.state

        def on_connect(client, userdata, flags, rc):
            print("Connected with result code "+str(rc))

        client = mqtt.Client()
        client.on_connect = on_connect

        client.connect(self.server, self.port, 60)

        while True:
            if "avgtemp" in state:
                client.publish(self.prefix+"/temperature", state['avgtemp'])
            else:
                client.publish(self.prefix+"/temperature", "N/A")

            if "settemp" in state:
                client.publish(self.prefix+"/settemp", state['settemp'])
            else:
                client.publish(self.prefix+"/settemp", "N/A")

            if "steam_mode" in state:
                client.publish(self.prefix+"/steam_mode", state['steam_mode'])
            else:
                client.publish(self.prefix+"/steam_mode", "N/A")

            if "is_awake" in state:
                client.publish(self.prefix+"/is_awake", state['is_awake'])
            else:
                client.publish(self.prefix+"/is_awake", "N/A")

            sleep(10)
