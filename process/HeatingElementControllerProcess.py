from time import sleep
from multiprocessing import Process

class HeatingElementControllerProcess(Process):
    def __init__(self, state, boiler):
        super(HeatingElementControllerProcess, self).__init__()

        self.boiler = boiler
        self.state = state
        boiler.heat_off()

    def run(self):
        try:
            while True:
                if self.state['steam_mode']:
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
                        if avgpid >= 20:
                            self.state['heating'] = True
                            self.boiler.heat_on()
                            sleep(1)
                        elif avgpid > 0 and avgpid < 20:
                            self.state['heating'] = True
                            self.boiler.heat_on()
                            sleep(avgpid / 20.)
                            self.boiler.heat_off()
                            sleep(1 - (avgpid / 20.))
                            self.state['heating'] = False
                        else:
                            self.boiler.heat_off()
                            self.state['heating'] = False
                            sleep(1)

        finally:
            self.boiler.heat_off()
            self.boiler.cleanup()
