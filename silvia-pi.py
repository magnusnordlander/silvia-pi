#!/usr/bin/python

import sys
from multiprocessing import Manager
from time import sleep, time
import os
import config as conf
import process
from hardware import temperature_sensor, boiler, button, solenoid, pump
from utils.const import *

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
            print(self.format_state(self.state))
#            print(self.state)

    def format_state(self, state):
        status_string = ""

        if state['is_awake']:
            status_string += "Awake, "
        else:
            status_string += "Asleep, "

        status_string += "T={}, <T>={}, <PID>={}, P={}, I={}, D={}, ".format(state['tempc'], state['avgtemp'], state['avgpid'], state['pterm'], state['iterm'], state['dterm'])

        if state['ignore_buttons']:
            status_string += "Buttons (ignored): <{}>, <{}>, <{}>, ".format(
                "BREW" if state['brew_button'] else "brew",
                "STEAM" if state['steam_button'] else "steam",
                "WATER" if state['water_button'] else "water"
            )
        else:
            status_string += "Buttons: <{}>, <{}>, <{}>, ".format(
                "BREW" if state['brew_button'] else "brew",
                "STEAM" if state['steam_button'] else "steam",
                "WATER" if state['water_button'] else "water"
            )

        status_string += "Tunings: {}, Steam mode: {}, Pre-infusion: {}, Brewing: {}".format(state['tunings'], "On" if state['steam_mode'] else "Off", "Yes" if state['use_preinfusion'] else "No", "Yes" if state['brewing'] else "No")

        try:
            status_string += ", Last shot time: {} s".format(round(state['last_brew_time'], 2))
        except KeyError:
            pass
        except TypeError:
            status_string += ", Current shot going on {} s".format(round(time() - state['brew_start']))

        return status_string


if __name__ == '__main__':


    manager = Manager()
    pidstate = manager.dict()
    pidstate['is_awake'] = True
    pidstate['i'] = 0
    pidstate['settemp'] = conf.set_temp
    pidstate['avgtemp'] = None
    pidstate['avgpid'] = 0.
    pidstate['steam_mode'] = False
    pidstate['ignore_buttons'] = False
    pidstate['use_preinfusion'] = conf.use_preinfusion
    pidstate['tunings'] = TUNINGS_COLD
    pidstate['dynamic_kp'] = 0.
    pidstate['dynamic_ki'] = 0.
    pidstate['dynamic_kd'] = 0.
    pidstate['use_pump_tunings'] = conf.use_pump_tunings

    if conf.test_hardware:
        sensor = temperature_sensor.EmulatedSensor(pidstate)
        boiler = boiler.EmulatedBoiler(sensor)
        brew_button = button.EmulatedRandomButton()
        steam_button = button.EmulatedRandomButton()
        water_button = button.EmulatedRandomButton()
        solenoid = solenoid.EmulatedSolenoid()
        pump = pump.EmulatedPump()
    else:
        boiler = boiler.GpioBoiler(conf.he_pin)
        sensor = temperature_sensor.Max31865Sensor(conf.temp_sensor_cs_pin, rtd_nominal=100.5)
        brew_button = button.GpioSwitchButton(conf.brew_button_pin)
        steam_button = button.GpioSwitchButton(conf.steam_button_pin)
        water_button = button.GpioSwitchButton(conf.water_button_pin)
        solenoid = solenoid.GpioSolenoid(conf.solenoid_pin)
        pump = pump.EmulatedPump()

    processes = {
        'InputReader': process.InputReaderProcess(pidstate, sensor, brew_button, steam_button, water_button, conf.fast_sample_time, conf.factor),
        'PID': process.SimplePidProcess(pidstate, conf.slow_sample_time, conf),
        'SteamControl': process.SteamControlProcess(pidstate, conf.slow_sample_time, conf.steam_low_temp, conf.steam_high_temp),
        'HeatingElement': process.HeatingElementControllerProcess(pidstate, boiler),
        'BrewControl': process.BrewControlProcess(pidstate, solenoid, pump, conf.preinfusion_time, conf.dwell_time, conf.fast_sample_time),
        'RestServer': process.RestServerProcess(pidstate, os.path.dirname(__file__) + '/www/', port=conf.port),
        'MQTTPublisher': process.MqttProcess.MqttPublishProcess(pidstate, server=conf.mqtt_server, prefix=conf.mqtt_prefix),
        'MQTTSubscriber': process.MqttProcess.MqttSubscribeProcess(pidstate, server=conf.mqtt_server, prefix=conf.mqtt_prefix)
    }

    watchdog = Watchdog(pidstate, processes)
    watchdog.run()
