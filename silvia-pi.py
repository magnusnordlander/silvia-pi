import asyncio
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
    await asyncio.sleep(0.5)
    for coro in coros:
        coro.publish_authoritative()

if __name__ == '__main__':
    bleak_logger = logging.getLogger('bleak')
    bleak_logger.setLevel(logging.WARN)

    loop = asyncio.get_event_loop()
    hub = PubSub.Hub()

    if conf.test_hardware:
        s = temperature_sensor.EmulatedSensor({})
        b = boiler.EmulatedBoiler(s)
        p = pump.EmulatedPump()
        v = solenoid.EmulatedSolenoid()
        d = display.EmulatedDisplay('/Users/magnusnordlander/emulated_display.jpg')
    else:
        s = temperature_sensor.Max31865Sensor(conf.temp_sensor_cs_pin, rtd_nominal=100.5)
        b = boiler.GpioBoiler(conf.he_pin)
        p = pump.GpioPump(conf.pump_pin)
        v = solenoid.GpioSolenoid(conf.solenoid_pin)
        d = display.EmulatedDisplay('/home/pi/silvia-pi/emulated_display.jpg')

    b.force_heat_off()
    p.stop_pumping()
    v.close()

    coros = [
        PigpioPins(hub, loop, host=conf.pigpio_host, port=conf.pigpio_port),
        TemperatureSensor(hub, s),
        SteamControlSignal(hub, conf.steam_set_point, conf.steam_delta),
        HeatingElementController(hub, b),
        ButtonControls(hub),
        SimplePidControlSignal(hub, (3.4, 0.3, 40.0), default_setpoint=conf.set_point),
        AcaiaScaleSensor(hub, conf.acaia_mac),
        MQTTProxy(hub, conf.mqtt_server, prefix=conf.mqtt_prefix, debug_mappings=True),
        ActuatorControl(hub, p, v),
        BrewControl(
            hub,
            default_use_preinfusion=conf.use_preinfusion,
            default_preinfusion_time=conf.preinfusion_time,
            default_dwell_time=conf.dwell_time
        ),
        BrewTimer(hub),
        WeightedShotController(hub, conf.weighted_shot_reaction_compensation),
        DisplayController(hub, d),
        BrewProfiler(hub, conf.brew_profile_directory)
    ]

    loop.run_until_complete(asyncio.gather(*functools.reduce(lambda carry, coro: carry + coro.pre_futures(), coros, [])))

    futures = functools.reduce(lambda carry, coro: carry + coro.futures(loop), coros, [])
    futures.append(printer(hub, frozenset([
        topics.TOPIC_CURRENT_BOILER_TEMPERATURE,
        topics.TOPIC_AVERAGE_BOILER_TEMPERATURE,
        topics.TOPIC_PID_AVERAGE_VALUE,
        topics.TOPIC_PID_VALUE,
        topics.TOPIC_STEAM_HE_ON,
        topics.TOPIC_HE_ON,
        topics.TOPIC_PID_TERMS,
    ])))
    futures.append(publish_initial_authoritative_state(coros))

    try:
        loop.run_until_complete(asyncio.gather(*futures))
        loop.run_forever()
    finally:
        b.force_heat_off()
        p.stop_pumping()
        v.close()
