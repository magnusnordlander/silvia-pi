from time import sleep, time
from multiprocessing import Process
from utils.const import *


class BrewControlProcess(Process):
    def __init__(self, state, solenoid, pump, weighted_shot_reaction_compensation, disable_buttons_during_weighted_shot, sample_time):
        super(BrewControlProcess, self).__init__()

        self.disable_buttons_during_weighted_shot = disable_buttons_during_weighted_shot
        self.weighted_shot_reaction_compensation = weighted_shot_reaction_compensation
        self.solenoid = solenoid
        self.pump = pump

        self.sample_time = sample_time
        self.state = state

        self.scale_tare = 0.
        self.auto_disabled_buttons = False

        self.prev_tunings = None

    def run(self):
        i=0
        lasttime = time()

        self.state['brewing'] = False
        self.state['hot_water'] = False
        prev_brew_state = False
        prev_hot_water_state = False


        self.state['pumping'] = False
        self.state['solenoid_open'] = False

        while True:
            if not self.state['ignore_buttons']:
                self.state['steam_mode'] = self.state['steam_button']

                if not self.state['brewing'] and self.state['brew_button']:
                    print("Button says start brew")
                    self.state['brewing'] = True
                elif self.state['brewing'] and not self.state['brew_button']:
                    print("Button says stop brew")
                    self.state['brewing'] = False

                # Brewing takes priority over hot water<
                if not self.state['brewing']:
                    if not self.state['hot_water'] and self.state['water_button']:
                        print("Button says start pumping hot water")
                        self.state['hot_water'] = True
                    elif self.state['hot_water'] and not self.state['water_button']:
                        print("Button says stop pumping hot water")
                        self.state['hot_water'] = False

            if self.state['brewing'] and prev_brew_state and self.state['brew_to_weight']:
                if (self.state['scale_weight'] - self.scale_tare) >= self.state['target_weight'] + self.weighted_shot_reaction_compensation:
                    print("Weight achieved (", (self.state['scale_weight'] - self.scale_tare), " over ", self.state['target_weight'], " stopping brew")
                    self.state['brewing'] = False

                    if self.auto_disabled_buttons:
                        self.auto_disabled_buttons = False
                        self.state['ignore_buttons'] = False

            if prev_brew_state != self.state['brewing']:
                if self.state['brewing']:
                    self.start_brew()
                else:
                    self.stop_brew()
                prev_brew_state = self.state['brewing']

            if not self.state['brewing'] and prev_hot_water_state != self.state['hot_water']:
                if self.state['hot_water']:
                    self.start_pump()
                else:
                    self.stop_pump()
                prev_hot_water_state = self.state['hot_water']

            sleeptime = lasttime + self.sample_time - time()
            if sleeptime < 0:
                sleeptime = 0
            sleep(sleeptime)
            i += 1
            lasttime = time()

    def start_brew(self):
        print("Starting brew")
        self.state['brew_stop'] = None
        self.state['last_brew_time'] = None
        self.state['brew_start'] = time()

        self.scale_tare = self.state['scale_weight']

        if self.disable_buttons_during_weighted_shot and self.state['brew_to_weight']:
            self.state['ignore_buttons'] = True
            self.auto_disabled_buttons = True

        self.open_solenoid()
        self.start_pump()
        if self.state['use_preinfusion']:
            sleep(self.state['preinfusion_time'])
            print("Pre-infusion done, dwelling")
            self.stop_pump()
            self.close_solenoid()
            sleep(self.state['dwell_time'])
            print("Continuing with the shot")
            self.open_solenoid()
            self.start_pump()

    def stop_brew(self):
        print("Stopping brew")
        self.state['brew_stop'] = time()
        self.state['last_brew_time'] = self.state['brew_stop'] - self.state['brew_start']
        self.stop_pump()
        self.close_solenoid()

    def start_pump(self):
        self.pump.start_pumping()
        self.state['pumping'] = True
        self.prev_tunings = self.state['tunings']
        if self.state['use_pump_tunings']:
            self.state['tunings'] = TUNINGS_PUMPING

    def stop_pump(self):
        self.pump.stop_pumping()
        self.state['pumping'] = False
        if self.prev_tunings is not None:
            self.state['tunings'] = self.prev_tunings
        self.prev_tunings = None

    def open_solenoid(self):
        self.solenoid.open()
        self.state['solenoid_open'] = True

    def close_solenoid(self):
        self.solenoid.close()
        self.state['solenoid_open'] = False
