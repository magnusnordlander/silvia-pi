#!/usr/bin/python

import sys
from multiprocessing import Manager
from time import sleep
import os
import config as conf
from process import HeatingElementControllerProcess, SimplePidProcess, MqttProcess, RestServerProcess, GPLPidprocess
import boiler
import temperature_sensor

class Watchdog:
    def __init__(self, state, process_dict):
        self.piderr = 0
        self.lasti = 0
        self.state = state
        self.process_dict = process_dict

    def start_all_processes(self):
        for process_name in self.process_dict:
            print("Starting " + process_name)
            self.process_dict[process_name].daemon = True
            self.process_dict[process_name].start()

    def print_process_state(self):
        for process_name in self.process_dict:
            print(process_name + ': ', self.process_dict[process_name].is_alive())

    def all_processes_alive(self):
        for process_name in self.process_dict:
            if not self.process_dict[process_name].is_alive():
                return False

        return True

    def check_pid_i(self):
        curi = self.state['i']
        if curi == self.lasti:
            self.piderr = self.piderr + 1
        else:
            self.piderr = 0

        self.lasti = curi

        if self.piderr > 9:
            print('ERROR IN PID THREAD, SHUTTING DOWN')
            sys.exit()

    def run(self):

        print("Starting Watchdog...")
        self.start_all_processes()

        self.lasti = self.state['i']
        sleep(1)

        print("Starting loop...")
        self.print_process_state()

        while self.all_processes_alive():
            self.check_pid_i()
            sleep(1)


if __name__ == '__main__':

    #  boiler = GpioBoiler(conf.he_pin)

    #  import board
    #  sensor = Max31865Sensor(board.D5, rtd_nominal=100.5)

    manager = Manager()
    pidstate = manager.dict()
    pidstate['is_awake'] = True
    pidstate['i'] = 0
    pidstate['settemp'] = conf.set_temp
    pidstate['avgpid'] = 0.


    sensor = temperature_sensor.EmulatedSensor(pidstate)
    boiler = boiler.EmulatedBoiler(sensor)


    processes = {
        'PID': SimplePidProcess(pidstate, sensor, conf),
#        'PID': GPLPidprocess(pidstate, sensor, conf),
        'HeatingElement': HeatingElementControllerProcess(pidstate, boiler),
#        'RestServer': RestServerProcess(pidstate, os.path.dirname(__file__) + '/www/', port=conf.port),
#        'MQTTPublisher': MqttProcess.MqttPublishProcess(pidstate, server="192.168.10.66", prefix="fakesilvia"),
#        'MQTTSubscriber': MqttProcess.MqttSubscribeProcess(pidstate, server="192.168.10.66", prefix="fakesilvia")
    }

    watchdog = Watchdog(pidstate, processes)
    watchdog.run()
