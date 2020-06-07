from time import sleep
from multiprocessing import Process

class HeatingElementControllerProcess(Process):
    def __init__(self, state, boiler):
        super(HeatingElementControllerProcess, self).__init__()

        self.boiler = boiler
        self.state = state
        self.state['he_follow_pump'] = True

        boiler.heat_off()

    def run(self):
        try:
            while True:
                try:
                    pumping = self.state['pumping']
                except KeyError:
                    pumping = False

                if self.state['he_follow_pump'] and pumping and self.state['avgtemp'] < 120:  # Just a sanity check to not run too hot
                    self.boiler.heat_on()
                    sleep(0.1)

                elif self.state['steam_mode']:
                    if self.state['steam_element_on']:
                        self.boiler.heat_on()
                    else:
                        self.boiler.heat_off()
                    sleep(0.1)

                else:
                    avgpid = self.state['avgpid']

                    if self.state['is_awake'] == False:
                        self.state['heating'] = False
                        self.boiler.heat_off()
                        sleep(1)
                    else:
                        if avgpid >= 100:
                            self.state['heating'] = True
                            self.boiler.heat_on()
                            sleep(1)
                        elif avgpid > 0 and avgpid < 100:
                            self.state['heating'] = True
                            self.boiler.heat_on()
                            sleep(avgpid / 100.)
                            self.boiler.heat_off()
                            sleep(1 - (avgpid / 100.))
                            self.state['heating'] = False
                        else:
                            self.boiler.heat_off()
                            self.state['heating'] = False
                            sleep(1)

        finally:
            self.boiler.heat_off()
            self.boiler.cleanup()
