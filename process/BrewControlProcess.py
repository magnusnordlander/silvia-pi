from time import sleep, time
from multiprocessing import Process


class BrewControlProcess(Process):
    def __init__(self, state, solenoid, pump, sample_time):
        super(BrewControlProcess, self).__init__()

        self.solenoid = solenoid
        self.pump = pump

        self.sample_time = sample_time
        self.state = state

    def run(self):
        i=0
        lasttime = time()

        self.state['brewing'] = False
        prev_brew_state = False

        while True:
            if not self.state['ignore_buttons']:
                self.state['steam_mode'] = self.state['steam_button']

                if not self.state['brewing'] and self.state['brew_button']:
                    print("Button says start brew")
                    self.state['brewing'] = True
                elif self.state['brewing'] and not self.state['brew_button']:
                    print("Button says stop brew")
                    self.state['brewing'] = False

            if prev_brew_state != self.state['brewing']:
                if self.state['brewing']:
                    self.start_brew()
                else:
                    self.stop_brew()
                prev_brew_state = self.state['brewing']

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
        self.solenoid.open()
        self.pump.start_pumping()

    def stop_brew(self):
        print("Stopping brew")
        self.state['brew_stop'] = time()
        self.state['last_brew_time'] = self.state['brew_stop'] - self.state['brew_start']
        self.pump.stop_pumping()
        self.solenoid.close()
