import asyncio
import apigpio_fork
import config as conf
from utils import topics, PubSub
import functools
from coroutines import *
from hardware import boiler, pump, solenoid, temperature_sensor, display
import logging


async def printer(hub, ignored_topics=frozenset()):
    with PubSub.Listener(hub) as queue:
        while True:
            key, msg = await queue.get()
            if key not in ignored_topics:
                print(f'Reader for key {key} got message: {msg}')


async def publish_initial_authoritative_state(coros):
    await asyncio.sleep(2)
    for coro in coros:
        coro.publish_authoritative()


async def safe_actuators(pi, solenoid_pin, pump_pin, he_pin):
    print("Safing actuators")
    await pi.write(he_pin, 0)
    await pi.write(pump_pin, 0)
    await pi.write(solenoid_pin, 0)

if __name__ == '__main__':
    bleak_logger = logging.getLogger('bleak')
    bleak_logger.setLevel(logging.WARN)

    loop = asyncio.get_event_loop()
    hub = PubSub.Hub()

    if conf.test_hardware:
        s = temperature_sensor.EmulatedSensor({})
        b = boiler.EmulatedBoiler(s)
        p = pump.EmulatedPump()
    else:
        s = temperature_sensor.Max31865Sensor(conf.boiler_temp_sensor_cs_pin, conf.group_temp_sensor_cs_pin, rtd_nominal_boiler=100.65, rtd_nominal_group=100.8)
        b = boiler.GpioBoiler(conf.he_pin)
        p = pump.GpioPump(conf.pump_pin)

    pi = apigpio_fork.Pi(loop)
    address = (conf.pigpio_host, conf.pigpio_port)
    loop.run_until_complete(pi.connect(address))
    loop.run_until_complete(safe_actuators(pi, conf.solenoid_pin, conf.pump_pin, conf.he_pin))

    dc = DisplayController(hub, pi, dev_num=1, cs_num=0, dc=12, res=22)

    coros = [
        PigpioPins(hub, pi),
        TemperatureSensor(hub, s),
        SteamControlSignal(hub, conf.steam_set_point, conf.steam_delta),
        HeatingElementController(hub, b),
        ButtonControls(hub),
        SimplePidControlSignal(hub, (3.4, 0.3, 40.0), default_setpoint=conf.set_point),
        AcaiaScaleSensor(hub, conf.acaia_mac),
        MQTTProxy(hub, conf.mqtt_server, prefix=conf.mqtt_prefix, debug_mappings=True),
        ActuatorControl(hub, pi, conf.pump_pin, conf.solenoid_pin),
        BrewControl(
            hub,
            default_use_preinfusion=conf.use_preinfusion,
            default_preinfusion_time=conf.preinfusion_time,
            default_dwell_time=conf.dwell_time
        ),
        BrewTimer(hub),
        WeightedShotController(hub, conf.weighted_shot_reaction_time),
        dc,
        BrewProfiler(hub, conf.brew_profile_directory)
    ]

    futures = functools.reduce(lambda carry, coro: carry + coro.futures(loop), coros, [])
    futures.append(printer(hub, frozenset([
        topics.TOPIC_CURRENT_BOILER_TEMPERATURE,
        topics.TOPIC_AVERAGE_BOILER_TEMPERATURE,
        topics.TOPIC_PID_AVERAGE_VALUE,
        topics.TOPIC_PID_VALUE,
        topics.TOPIC_STEAM_HE_ON,
        topics.TOPIC_HE_ON,
        topics.TOPIC_PID_TERMS,
        topics.TOPIC_CURRENT_GROUP_TEMPERATURE,
        topics.TOPIC_ALL_TEMPERATURES,
    ])))
    futures.append(publish_initial_authoritative_state(coros))

    try:
        loop.run_until_complete(asyncio.gather(*futures))
        loop.run_forever()
    finally:
        loop.run_until_complete(safe_actuators(pi, conf.solenoid_pin, conf.pump_pin, conf.he_pin))
        loop.run_until_complete(dc.close_handle())
