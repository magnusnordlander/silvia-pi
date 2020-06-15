import asyncio
import apigpio
import config as conf
from utils import topics, PubSub
from functools import partial
from coroutines import *
from hardware import boiler, pump, solenoid, temperature_sensor, display
import logging


async def printer(hub, ignored_topics=frozenset()):
    with PubSub.Listener(hub) as queue:
        while True:
            key, msg = await queue.get()
            if key not in ignored_topics:
                print(f'Reader for key {key} got message: {msg}')

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

    b.heat_off()
    p.stop_pumping()
    v.close()

    pins = PigpioPins(loop, hub)
    temp_sensor = TemperatureSensor(hub, s)
    steam_control = SteamControlSignal(hub)
    he_controller = HeatingElementController(hub, b)
    button_controls = ButtonControls(hub)
    pid_controller = SimplePidControlSignal(hub, (3.4, 0.3, 40.0))
    scale_sensor = AcaiaScaleSensor(hub, conf.acaia_mac)
    mqtt_proxy = MQTTProxy(hub, conf.mqtt_server, prefix=conf.mqtt_prefix, debug_mappings=True)
    actuator_control = ActuatorControl(hub, p, v)
    brew_control = BrewControl(
        hub,
        default_use_preinfusion=conf.use_preinfusion,
        default_preinfusion_time=conf.preinfusion_time,
        default_dwell_time=conf.dwell_time
    )
    brew_timer = BrewTimer(hub)
    weighted_shots = WeightedShotController(hub)
    display_controller = DisplayController(hub, d)

    loop.run_until_complete(asyncio.gather(*pins.pre_futures()))

    futures = []
    futures += pins.futures()
    futures += temp_sensor.futures()
    futures += steam_control.futures()
    futures += he_controller.futures()
    futures += button_controls.futures()
    futures += pid_controller.futures()
    futures += scale_sensor.futures(loop)
    futures += mqtt_proxy.futures()
    futures += actuator_control.futures()
    futures += brew_control.futures()
    futures += brew_timer.futures()
    futures += weighted_shots.futures()
    futures += display_controller.futures()
    futures.append(printer(hub, frozenset([
        topics.TOPIC_CURRENT_TEMPERATURE,
        topics.TOPIC_AVERAGE_TEMPERATURE,
        topics.TOPIC_PID_AVERAGE_VALUE,
        topics.TOPIC_PID_VALUE,
        topics.TOPIC_STEAM_HE_ON,
        topics.TOPIC_HE_ON
    ])))

    try:
        loop.run_until_complete(asyncio.gather(*futures))
        loop.run_forever()
    finally:
        b.heat_off()
        p.stop_pumping()
        v.close()
