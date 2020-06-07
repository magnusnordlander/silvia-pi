import sys
from time import sleep, time
from math import isnan
from multiprocessing import Process
from utils import ResizableRingBuffer, topics
import paho.mqtt.client as mqtt

class InputReaderProcess(Process):
    def __init__(self, mqtt_connection, temperature_sensor, brew_button, steam_button, water_button):
        super(InputReaderProcess, self).__init__()

        self.mqtt_connection = mqtt_connection
        self.temperature_sensor = temperature_sensor
        self.brew_button = brew_button
        self.steam_button = steam_button
        self.water_button = water_button
        self.temphist = ResizableRingBuffer(3)

    def run(self):

        def on_connect(client, userdata, flags, rc):
            print("Connected with result code "+str(rc))

        client = mqtt.Client()
        client.on_connect = on_connect

        client.connect(self.mqtt_connection['server'], self.mqtt_connection['port'], 60)

        while True:
            client.publish(topics.TOPIC_COFFEE_BUTTON, self.brew_button.button_state())
            client.publish(topics.TOPIC_STEAM_BUTTON, self.steam_button.button_state())
            client.publish(topics.TOPIC_WATER_BUTTON, self.water_button.button_state())

            sleep(1)