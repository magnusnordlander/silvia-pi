import asyncio
from utils import topics, PubSub
import time
from coroutines import Base
import csv
import json
import os


class BrewProfiler(Base):
    def __init__(self, hub, output_directory, post_brew_profiling_time=3.0):
        super().__init__(hub)
        self.post_brew_profiling_time = post_brew_profiling_time
        self.output_directory = output_directory

        self.profiling = False
        self.current_brew_data = []
        self.current_brew_metadata = {}

        # We'll be triggering on temperature changes, everything else is collected as an ivar
        self.define_ivar('current_avgpid', topics.TOPIC_PID_AVERAGE_VALUE)
        self.define_ivar('current_weight', topics.TOPIC_SCALE_WEIGHT)
        self.define_ivar('solenoid', topics.TOPIC_SOLENOID_OPEN)
        self.define_ivar('pump', topics.TOPIC_PUMP_ON)

        # Metadata
        self.define_ivar('enable_weighted_shots', topics.TOPIC_ENABLE_WEIGHTED_SHOT, False)
        self.define_ivar('target_weight', topics.TOPIC_TARGET_WEIGHT, 0.0)
        self.define_ivar('scale_connected', topics.TOPIC_SCALE_CONNECTED, False)
        self.define_ivar('preinfusion', topics.TOPIC_USE_PREINFUSION)
        self.define_ivar('preinfusion_time', topics.TOPIC_PREINFUSION_TIME)
        self.define_ivar('dwell_time', topics.TOPIC_DWELL_TIME)
        self.define_ivar('tunings', topics.TOPIC_PID_TUNINGS)
        self.define_ivar('responsiveness', topics.TOPIC_PID_RESPONSIVENESS)

    async def start_profiling(self):
        with PubSub.Subscription(self.hub, topics.TOPIC_START_BREW) as queue:
            while True:
                await queue.get()

                if self.enable_weighted_shots and self.scale_connected:
                    self.profiling = True

                    self.current_brew_metadata['target_weight'] = self.target_weight
                    self.current_brew_metadata['start_time'] = time.time()
                    self.current_brew_metadata['preinfusion'] = self.preinfusion
                    self.current_brew_metadata['preinfusion_time'] = self.preinfusion_time
                    self.current_brew_metadata['dwell_time'] = self.dwell_time
                    self.current_brew_metadata['tunings'] = self.tunings
                    self.current_brew_metadata['responsiveness'] = self.responsiveness

    async def stop_profiling(self):
        with PubSub.Subscription(self.hub, topics.TOPIC_STOP_BREW) as queue:
            while True:
                await queue.get()

                if self.profiling:
                    self.current_brew_metadata['stop_time'] = time.time()
                    self.current_brew_metadata['stop_weight'] = self.current_weight

                    await asyncio.sleep(self.post_brew_profiling_time)

                    self.current_brew_metadata['final_weight'] = self.current_weight

                    brew_data = self.current_brew_data
                    metadata = self.current_brew_metadata
                    self.reset()

                    self.store(brew_data, metadata)

    async def temperature_update(self):
        with PubSub.Subscription(self.hub, topics.TOPIC_ALL_TEMPERATURES) as queue:
            while True:
                temp_boiler, temp_group = await queue.get()

                if self.profiling:
                    self.current_brew_data.append([time.time(), temp_boiler, temp_group, self.current_weight, self.current_avgpid, self.solenoid, self.pump])

    def store(self, brew_data, metadata):
        base_filename = self.base_filename(metadata)
        data_filename = "{}.brewfile_v1.csv".format(base_filename)
        metadata_filename = "{}.meta_v1.json".format(base_filename)

        with open(self.output_directory+metadata_filename, 'w') as fp:
            json.dump(metadata, fp)
        os.chmod(self.output_directory+metadata_filename, 0o666)

        with open(self.output_directory+data_filename, 'w') as fp:
            wtr = csv.writer(fp, delimiter=',', lineterminator='\n')
            wtr.writerow(["Time", "Boiler Temperature", "Group Temperature", "Weight", "Avg. PID", "Solenoid", "Pump"])
            for r in brew_data:
                wtr.writerow(r)

    def base_filename(self, metadata):
        return "brew_{}".format(metadata['start_time'])

    def reset(self):
        self.profiling = False
        self.current_brew_data = []
        self.current_brew_metadata = {}

    def futures(self, loop):
        return [
            *super(BrewProfiler, self).futures(loop),
            self.start_profiling(),
            self.stop_profiling(),
            self.temperature_update()
        ]
