# silvia-pi
This is kindof-sortof a fork of [brycesub/silvia-pi](https://github.com/brycesub/silvia-pi). I say kindof-sortof because really the only two things remaining at this point are some of the PID code and the name. Big kudos to brycesub though.

I've *heavily* modified this project to suit my own fancy. Don't expect any of the documentation to be correct, 
or to be able to actually use this code. Also, I've significantly rewired my Silvia compared to both the stock setup
and to the setup described in the original README, so have fun reverse-engineering my wiring from the code. (Also, don't attempt to rewire your machine unless you *really know what you're doing*. The internal components run on mains voltage, in a hot and wet environment. Mains power can kill you.)

At some point in the future, I may make this more usable by others, but that point is not now.

Caveat emptor.

### Branches
* You're currently looking at the master branch. It's what I'm currently running on my espresso machine. Consider it beta quality *at best*.
* There's the multiprocess branch, which is an older version, more architecturally similar to brycesub/silvia-pi

### Current Hardware
* Raspberry Pi Zero W
* Adafruit PT100 RTD Temperature Sensor Amplifier - MAX31865
* ETP-RT-4-24-PT100B - SMT Ring Terminal Probe -40 °C 250 °C Pt100, Variohm EuroSensor (boiler sensor)
* Crydom D2425D Dual SSR (Controls heater and solenoid)
    * Adafruit BSS138 4-channel I2C-safe Bi-directional Logic Level Converter (I didn't realize the D2425D required >4 V for control)
* Crydom EZ240D5 SSR (Controls pump)
    * Also connected through the BSS138, but doesn't technically have to be
* Acaia Lunar
* 128x64 SPI OLED, SSD1306 controller (Super weird one too, without a CS pin)
* Another Adafruit MAX31865 sensor amplifier (for group head sensor)
* PTFM101T1A0 PT100,1.2X4.0,T thermocouple (group head sensor)

### Upcoming Hardware
* Adafruit ADS1083 4 channel ADC (Have it, but haven't implemented anything
* MIPAF1XX250PSAAX pressure transducer (Have it, but haven't installed it)

### Dismissed ideas
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
* Add reaction time compensation for weighted shots
* asyncio instead of multiprocess
* 128x64 SPI OLED display
* Second temperature sensor near group head

### In progress
* Dynamic reaction time compensation for weighted shots
   * Still haven't decided whether to project the shots as linear or polynomial, linear seems to work well for well-extracting shots, weird shots sometimes get polynomial
* Pressure gauge
    * ~~Sensata 116CP or 60CP seems like good choices, but hard to come by~~ Haven't even been able to find in small quantities, not to mention that I don't know the price
    * ~~BDSensors DMP331P or DS200P could also be good choices~~ Too expensive (~$400)
    * Honeywell MIP series will do. Given that it tops out at 125°C, it'll have to be mounted by the pump though.
      * Ideally MIPAG1XX016BSAAX or MIPAG1XX016BAAAX, but it'll likely be MIPAF1XX250PSAAX due to it being easier to source
      * https://www.mouser.se/datasheet/2/187/honeywell-sensing-heavy-duty-pressure-mip-series-d-1760329.pdf
      * Also needs an ADC
* ADC for Liquid level sensor and pressure gauge: Adafruit ADS1015. Needs additional BSS138.

### If I feel like it
* Liquid level sensor
    * eTape?
* GraphQL API
* React frontend

### IO Allocations

* GPIO00 - I2C
* GPIO01 - I2C
* GPIO02 - I2C SDA
* GPIO03 - I2C SCL
* GPIO04 - Heating element SSR Output
* GPIO05 - Steam button input
* GPIO06 - Water button input
* GPIO07 - SPI0CE1 - Unusable
* GPIO08 - SPI0CE0 - Unusable
* GPIO09 - SPI0MISO - RTD SPI
* GPIO10 - SPI0MOSI - RTD SPI
* GPIO11 - SPI0SCLK - RTD SPI
* GPIO12 - Display DC
* GPIO13 - Group RTD CE
* GPIO14 - Pump SSR Output
* GPIO15 - Solenoid SSR Output
* GPIO16 - SPI1CE2 - Unusable
* GPIO17 - SPI1CE1 - Unusable
* GPIO18 - SPI1CE0 - Unusable
* GPIO19 - SPI1MISO - Unusable
* GPIO20 - SPI1MOSI - Display SPI
* GPIO21 - SPI1SCLK - Display SPI
* GPIO22 - Display RES
* GPIO23 - Red button input
* GPIO24 - Blue button input
* GPIO25 - White button input
* GPIO26 - Boiler RTD CE
* GPIO27 - Brew button Input

#### I/O Notes
* Is GPIO00 and GPIO01 really needed for I2C?
* SPI0CE0 and SPI0CE1... Why can't I just use them for the RTDs? (I did try)
* The MAX31865 requires SPI Mode 1 or 3, meaning they can only be on SPI0
* The display is weird, it doesn't have a CE pin, so it uses all 3 chip selects of SPI1
   * If I want other SPI accessories, I'll either need to replace the display or to see if I can solder a CE pin on there

#### Super weird edge cases no one but me should worry about
* If we're already running the water pump and start brewing, what should happen?
    * We should open the solenoid too
    * When brewing stops (either due to actually stopping the brew, or due to preinfusion), we stop pumping. There's no practical use case for remembering the previous pump state.
    
