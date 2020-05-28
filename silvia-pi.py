#!/usr/bin/python

def wakeup(dummy,state):
  state['is_awake'] = True

def gotosleep(dummy,state):
  state['is_awake'] = False

def init_heat():
  import RPi.GPIO as GPIO
  GPIO.setmode(GPIO.BCM)
  GPIO.setup(conf.he_pin, GPIO.OUT)

def heat_on():
  import RPi.GPIO as GPIO
  print("Heat on")
  GPIO.output(conf.he_pin,1)

def heat_off():
  import RPi.GPIO as GPIO
  print("Heat off")
  GPIO.output(conf.he_pin,0)

def cleanup_heat():
  import RPi.GPIO as GPIO
  GPIO.cleanup()

def he_control_loop(dummy,state):
  from time import sleep
  import config as conf

  init_heat()
  heat_off()

  heating = False

  try:
    while True:
      avgpid = state['avgpid']

      if state['is_awake'] == False :
        state['heating'] = False
        heat_off()
        sleep(1)
      else:
        if avgpid >= 100 :
          state['heating'] = True
          heat_on()
          sleep(1)
        elif avgpid > 0 and avgpid < 100:
          state['heating'] = True
          heat_on()
          sleep(avgpid/100.)
          heat_off()
          sleep(1-(avgpid/100.))
          state['heating'] = False
        else:
          heat_off()
          state['heating'] = False
          sleep(1)

  finally:
    heat_off()
    cleanup_heat()

def init_temp():
  import board
  import busio
  import digitalio
  
  import adafruit_max31865
  # Initialize SPI bus and sensor.
  spi = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)
  cs = digitalio.DigitalInOut(board.D5)  # Chip select of the MAX31865 board.
  sensor = adafruit_max31865.MAX31865(spi, cs, rtd_nominal=100.5, wires=2)
  return sensor

def get_temp_c(sensor):
  return sensor.temperature

def pid_loop(dummy,state):
  import sys
  from time import sleep, time
  from math import isnan
  import PID as PID
  import config as conf

#  sys.stdout = open("pid.log", "a")
#  sys.stderr = open("pid.err.log2", "a")

  sensor = init_temp()

  print("got sensor:", sensor)

  pid = PID.PID(conf.Pc,conf.Ic,conf.Dc)
  pid.SetPoint = state['settemp']
  pid.setSampleTime(conf.sample_time*5)

  nanct=0
  i=0
  j=0
  pidhist = [0.,0.,0.,0.,0.,0.,0.,0.,0.,0.]
  avgpid = 0.
  temphist = [0.,0.,0.,0.,0.]
  avgtemp = 0.
  lastsettemp = state['settemp']
  lasttime = time()
  sleeptime = 0
  iscold = True
  iswarm = False
  lastcold = 0
  lastwarm = 0

  try:
    while True : # Loops 10x/second
      tempc = get_temp_c(sensor)
      if isnan(tempc) :
        nanct += 1
        if nanct > 100000 :
          sys.exit
        continue
      else:
        nanct = 0

      temphist[i%5] = tempc
      avgtemp = sum(temphist)/len(temphist)

      if avgtemp < 40 :
        lastcold = i

      if avgtemp > 90 :
        lastwarm = i

      if iscold and (i-lastcold)*conf.sample_time > 60*15 :
        pid = PID.PID(conf.Pw,conf.Iw,conf.Dw)
        pid.SetPoint = state['settemp']
        pid.setSampleTime(conf.sample_time*5)
        iscold = False

      if iswarm and (i-lastwarm)*conf.sample_time > 60*15 : 
        pid = PID.PID(conf.Pc,conf.Ic,conf.Dc)
        pid.SetPoint = state['settemp']
        pid.setSampleTime(conf.sample_time*5)
        iscold = True

      if state['settemp'] != lastsettemp :
        pid.SetPoint = state['settemp']
        lastsettemp = state['settemp']

      if i%10 == 0 :
        pid.update(avgtemp)
        pidout = pid.output
        pidhist[int(i/10%10)] = pidout
        avgpid = sum(pidhist)/len(pidhist)

      state['i'] = i
      state['tempc'] = round(tempc,2)
      state['avgtemp'] = round(avgtemp,2)
      state['pidval'] = round(pidout,2)
      state['avgpid'] = round(avgpid,2)
      state['pterm'] = round(pid.PTerm,2)
      if iscold :
        state['iterm'] = round(pid.ITerm * conf.Ic,2)
        state['dterm'] = round(pid.DTerm * conf.Dc,2)
      else :
        state['iterm'] = round(pid.ITerm * conf.Iw,2)
        state['dterm'] = round(pid.DTerm * conf.Dw,2)
      state['iscold'] = iscold

      print(time(), state)

      sleeptime = lasttime+conf.sample_time-time()
      if sleeptime < 0 :
        sleeptime = 0
      sleep(sleeptime)
      i += 1
      lasttime = time()

  finally:
    pid.clear

def rest_server(dummy,state):
  from bottle import route, run, get, post, request, static_file, abort
  from subprocess import call
  from datetime import datetime
  import config as conf
  import os

  basedir = os.path.dirname(__file__)
  #wwwdir = basedir+'/www/'
  wwwdir = "/home/pi/silvia-pi/www"

  @route('/home')
  def docroot():
    return static_file('index.html',wwwdir)

  @route('/<filepath:path>')
  def servfile(filepath):
    return static_file(filepath,wwwdir)

  @route('/curtemp')
  def curtemp():
    return str(state['avgtemp'])

  @get('/settemp')
  def settemp():
    return str(state['settemp'])

  @post('/settemp')
  def post_settemp():
    try:
      settemp = float(request.forms.get('settemp'))
      if settemp >= 90 and settemp <= 125 :
        state['settemp'] = settemp
        return str(settemp)
      else:
        abort(400,'Set temp out of range 90-125.')
    except:
      abort(400,'Invalid number for set temp.')

  @get('/is_awake')
  def get_is_awake():
    return str(state['is_awake'])

  @get('/allstats')
  def allstats():
    return dict(state)

  @get('/healthcheck')
  def healthcheck():
    return 'OK'

  run(host='0.0.0.0',port=conf.port,server='cheroot')

def mqtt_subscribe_loop(dummy, state):
  import paho.mqtt.client as mqtt
  def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe("silvia/settemp/set")
    client.subscribe("silvia/is_awake/set")

  # The callback for when a PUBLISH message is received from the server.
  def on_message(client, userdata, msg):
    if msg.topic == "silvia/settemp/set":
      state['settemp'] = float(msg.payload)
      client.publish("silvia/settemp", state['settemp'])
    elif msg.topic == "silvia/is_awake/set":
      state['is_awake'] = bool(distutils.util.strtobool(msg.payload))
      client.publish("silvia/is_awake", state['is_awake'])
    print(msg.topic+" "+str(msg.payload))

  client = mqtt.Client()
  client.on_connect = on_connect
  client.on_message = on_message

  client.connect("192.168.10.66", 1883, 60)

  # Blocking call that processes network traffic, dispatches callbacks and
  # handles reconnecting.
  # Other loop*() functions are available that give a threaded interface and a
  # manual interface.
  client.loop_forever()

def mqtt_publish_loop(dummy, state):
  import paho.mqtt.client as mqtt
  def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

  client = mqtt.Client()
  client.on_connect = on_connect

  client.connect("192.168.10.66", 1883, 60)

  while True:
    if "avgtemp" in state:
      client.publish("silvia/temperature", state['avgtemp'])
    else:
      client.publish("silvia/temperature", "N/A")

    if "settemp" in state:
      client.publish("silvia/settemp", state['settemp'])
    else:
      client.publish("silvia/settemp", "N/A")

    if "is_awake" in state:
      client.publish("silvia/is_awake", state['is_awake'])
    else:
      client.publish("silvia/is_awake", "N/A")

    sleep(10)

if __name__ == '__main__':
  from multiprocessing import Process, Manager
  from time import sleep
  from urllib.request import urlopen
  import config as conf

  manager = Manager()
  pidstate = manager.dict()
  pidstate['is_awake'] = True
  pidstate['i'] = 0
  pidstate['settemp'] = conf.set_temp
  pidstate['avgpid'] = 0.

  print("Starting PID thread...")
  p = Process(target=pid_loop,args=(1,pidstate))
  p.daemon = True
  p.start()

  print("Starting HE Control thread...")
  h = Process(target=he_control_loop,args=(1,pidstate))
  h.daemon = True
  h.start()

  print("Starting REST Server thread...")
  r = Process(target=rest_server,args=(1,pidstate))
  r.daemon = True
  r.start()

  print("Starting MQTT Publish thread...")
  mp = Process(target=mqtt_publish_loop,args=(1,pidstate))
  mp.daemon = True
  mp.start()

  print("Starting MQTT Subscribe thread...")
  ms = Process(target=mqtt_subscribe_loop,args=(1,pidstate))
  ms.daemon = True
  ms.start()

  #Start Watchdog loop
  print("Starting Watchdog...")
  piderr = 0
  weberr = 0
  weberrflag = 0
  urlhc = 'http://localhost:'+str(conf.port)+'/healthcheck'

  lasti = pidstate['i']
  sleep(1)

  print("Starting loop...", p.is_alive(), h.is_alive(), r.is_alive(), mp.is_alive(), ms.is_alive())
  while p.is_alive() and h.is_alive() and r.is_alive() and mp.is_alive() and ms.is_alive():
    curi = pidstate['i']
    if curi == lasti :
      piderr = piderr + 1
    else :
      piderr = 0

    lasti = curi

    if piderr > 9 :
      print('ERROR IN PID THREAD, RESTARTING')
      p.terminate()

    try:
      hc = urlopen(urlhc,timeout=2)
    except:
      weberrflag = 1
    else:
      if hc.getcode() != 200 :
        weberrflag = 1

    if weberrflag != 0 :
      weberr = weberr + 1

    if weberr > 9 :
      print('ERROR IN WEB SERVER THREAD, RESTARTING')
      r.terminate()

    weberrflag = 0

    sleep(1)
