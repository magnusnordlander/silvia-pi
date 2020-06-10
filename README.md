# silvia-pi
A Raspberry Pi modification to the Rancilio Silvia Espresso Machine implementing PID temperature control.

## Magnus' mods
I've *heavily* modified this project to suit my own fancy. Don't expect any of the documentation to be correct, 
or to be able to actually use this code. Also, I've significantly rewired my Silvia compared to both the stock setup
and to the setup described in the original README, so have fun reverse-engineering my wiring from the code. (Also, don't attempt to rewire your machine unless you *really know what you're doing*. The internal components run on mains voltage, in a hot and wet environment. Mains power can kill you.)

At some point in the future, I may make this more usable by others, but that point is not now.

Caveat emptor.

### Current Hardware
* Raspberry Pi Zero W
* Adafruit PT100 RTD Temperature Sensor Amplifier - MAX31865
* ETP-RT-4-24-PT100B - SMT Ring Terminal Probe -40 °C 250 °C Pt100, Variohm EuroSensor
* Crydom D2425D Dual SSR (Controls heater and solenoid)
    * Adafruit BSS138 4-channel I2C-safe Bi-directional Logic Level Converter (I didn't realize the D2425D required >4 V for control)
* Crydom EZ240D5 SSR (Controls pump)
    * Also connected through the BSS138, but doesn't technically have to be
* Acaia Lunar

### Upcoming Hardware
* 128x64 SPI OLED, SSD1302 controller
* ~~Proportional relay~~ (Dismissed due to non-proportional relays providing good enough control, and proportional relays being super pricy)
   * MCPC2450A or similar
   * Adafruit MCP4725 for control

### Done
* Remove scheduling
   * I'd rather do scheduling via MQTT through Home Assistant
* Switch to Celsius
* Use a MAX31865 temperature sensor
* MQTT publishing and control
* A whole lot of code restructuring
* Steam temperature control
* Digital controls
   * Rewire the entire thing to control the pump, the boiler and the solenoid separately, and read the button states using GPIO
* Preinfusion
* Smart scale integration (Acaia)

### In progress (not always in pushed branches)
* Add reaction time compensation for weighted shots
* 128x64 SPI OLED display
* asyncio instead of multiprocess

### If I feel like it
* Second temperature sensor near group head?
* Liquid level sensor
    * eTape?
* Pressure gauge
    * Sensata 116CP or 60CP seems like good choices, but hard to come by
    * BDSensors DMP331P or DS200P could also be good choices
* GraphQL API
* React frontend

## Original README (Mostly not applicable anymore)

#### Currently Implemented Features:
* Brew temperature control
* RESTful API
* Web interface for displaying temperature and other statistics
* Programmable machine warm-up/wake-up

#### Planned Features:
* Steam temperature control
* Timed shots with pre-infusion
* Digital pressure gauge

#### Dashboard
<img src="https://github.com/brycesub/silvia-pi/blob/master/media/silvia_dashboard.gif" width=800 />

#### Hardware
* Raspberry Pi 2
  * $35 - http://www.amazon.com/Raspberry-Pi-Model-Project-Board/dp/B00T2U7R7I
  * $5 - Raspberry Pi Zero should work too
* Wi-Fi Adapter that works with Raspbian
  * $10 - http://www.amazon.com/Edimax-EW-7811Un-150Mbps-Raspberry-Supports/dp/B003MTTJOY or
  * $10 - http://www.amazon.com/Tenda-150Mbps-Wireless-Adapter-W311MI/dp/B006GCYAOI
* Power Adapter
  * Any Micro USB 5v / 2A supply will do, the longer the cable the better
  * $9 - http://www.amazon.com/CanaKit-Raspberry-Supply-Adapter-Charger/dp/B00GF9T3I0
* Micro SD Card
  * 4GB minimum, 8GB Class 10 recommended
  * $7 - http://www.amazon.com/Samsung-Class-Adapter-MB-MP16DA-AM/dp/B00IVPU7KE
* Solid State Relay - For switching on and off the heating element
  * $10 - https://www.sparkfun.com/products/13015
* Thermocouple Amplifier - For interfacing between the Raspberry Pi and Thermocouple temperature probe
  * $15 - https://www.sparkfun.com/products/13266
* Type K Thermocouple - For accurate temperature measurement
  * $15 - http://www.auberins.com/index.php?main_page=product_info&cPath=20_3&products_id=307
* Ribbon Cable - For connecting everything together
  * $7 - http://www.amazon.com/Veewon-Flexible-Multicolored-Female-Breadboard/dp/B00N7XX4XM
    * Female to Female if using the Raspberry Pi 2
  * $5 - http://www.amazon.com/uxcell-Width-Colorful-Flexible-Ribbon/dp/B00BWFY6JI
    * Bare wire if using the Raspberry Pi Zero
* 14 gauge wire - For connecting the A/C side of the relay to the circuit
  * $5 - Hardware Store / Scrap
    * Don't skimp here.  Remember this wire will be in close proximit to a ~240*F boiler

#### Hardware Installation
[Installation Instructions / Pictures](http://imgur.com/a/3WLVt)

#### Circuit Diagram
High-level circuit diagram:

![Circuit Diagram](media/circuit.png?raw=true "Circuit Diagram")

#### Software
* OS - Raspbian Jessie
  * Full - https://downloads.raspberrypi.org/raspbian_latest
  * Lite (for smaller SD Cards) - https://downloads.raspberrypi.org/raspbian_lite_latest

Install Raspbian and configure Wi-Fi and timezone.

#### silvia-pi Software Installation Instructions
Execute on the pi bash shell:
````
sudo apt-get -y update
sudo apt-get -y upgrade
sudo apt-get -y install rpi-update git build-essential python-dev python-smbus python-pip
sudo rpi-update
sudo bash -c 'echo "dtparam=spi=on" >> /boot/config.txt'
sudo reboot
````

After the reboot:
````
sudo git clone https://github.com/brycesub/silvia-pi.git /root/silvia-pi
sudo /root/silvia-pi/setup.sh
````
This last step will download the necessariy python libraries and install the silvia-pi software in /root/silvia-pi

It also creates an entry in /etc/rc.local to start the software on every boot.

#### API Documentation

##### GET /allstats
Returns JSON of all the following statistics:
* i : Current loop iterator value (increases 10x per second)
* tempf : Temperature in °F
* avgtemp : Average temperature over the last 10 cycles (1 second) in °F
* settemp : Current set (goal) temperature in °F
* iscold : True if the temp was <120°F in the last 15 minutes
* hestat : 0 if heating element is currently off, 1 if heating element is currently on
* pidval : PID output from the last cycle
* avgpid : Average PID output over the last 10 cycles (1 second)
* pterm : PID P Term value (Proportional error)
* iterm : PID I Term value (Integral error)
* dterm : PID D Term value (Derivative error)
* snooze : Current or last snooze time, a string in the format HH:MM (24 hour)
* snoozeon : true if machine is currently snoozing, false if machine is not snoozing

##### GET /curtemp
Returns string of the current temperature in °F

##### GET /settemp
Returns string of the current set (goal) temperature in °F

##### POST /settemp
Expects one input 'settemp' with a value between 200-260.  
Sets the set (goal) temperature in °F
Returns the set temp back or a 400 error if unsuccessful.

##### GET /snooze
Returns string of the current or last snooze time formatted "HH:MM" (24 hour).  
e.g. 13:00 if snoozing until 1:00 PM local time.

##### POST /snooze
Expects one input 'snooze', a string in the format "HH:MM" (24 hour).  
This enables the snooze function, the machine will sleep until the time specified.  
Returns the snooze time set or 400 if passed an invalid input.

##### POST /resetsnooze
Disables/cancels the current snooze functionality.  
Returns true always.

##### GET /restart
Issues a reboot command to the Raspberry Pi.

##### GET /healthcheck
A simple healthcheck to see if the webserver thread is repsonding.  
Returns string 'OK'.
