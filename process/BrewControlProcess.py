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
        temphist = [0.,0.,0.,0.,0.]
        avgtemp = 0.
        i=0
        lasttime = time()

        self.state['brewing'] = False

        while True:
            if not self.state['brewing'] and self.state['brew_button']:
                print("Starting brew")

                self.state['brewing'] = True

                self.solenoid.open()
                self.pump.start_pumping()
            elif self.state['brewing'] and not self.state['brew_button']:
                print("Stopping brew")

                self.state['brewing'] = False

                self.solenoid.close()
                self.pump.stop_pumping()

            sleeptime = lasttime + self.sample_time - time()
            if sleeptime < 0:
                sleeptime = 0
            sleep(sleeptime)
            i += 1
            lasttime = time()
