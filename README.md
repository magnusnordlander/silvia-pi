# silvia-pi
This is kindof-sortof a fork of [brycesub/silvia-pi](https://github.com/brycesub/silvia-pi). I say kindof-sortof because really the only two things remaining at this point are some of the PID code and the name. Big kudos to brycesub though.

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
* Another Adafruit MAX31865 sensor amplifier
* PTFM101T1A0 PT100,1.2X4.0,T thermocouple
* Adafruit ADS1083 4 channel ADC
* MIPAF1XX250PSAAX pressure transducer
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
* 128x64 SPI OLED display *Performance problems. This'll probably require the asyncio refactoring to work well.*

### In progress
* Second temperature sensor near group head?
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
* SPI0CS1 (CS Pin 5): MAX31865 temp sensor 1
   * GPIO10
   * GPIO9
   * GPIO11
   * CS: GPIO5 (Why aren't I using the standard GPIO8? reallocate)
* SPI0CS2: MAX31865 temp sensor 2 (not yet implemented)
   * GPIO10
   * GPIO9
   * GPIO11
   * CS: GPI07
* SPI1CS1: SSD1302 128x64 SPI OLED (implementation in progress)
   * GPIO19
   * GPIO20
   * GPIO21
   * CS: GPIO18
* I2C: ADC for pressure sensor (not yet implemented)
   * GPIO0
   * GPIO1
   * GPIO2
   * GPIO3
* GPIO18: Heating element (via BSS138) *Conflict with standard SPI1CE0, reallocate to GPIO4*
* GPIO14: Solenoid (via BSS138)
* GPIO15: Pump (via BSS138)
* GPIO21: Brew button *Conflict with SPI1, reallocate to GPIO5*
* GPIO16: Steam button *Conflict with SPI1, reallocate to GPIO6*
* GPIO20: Water button *Reallocate to GPIO13*

#### Free GPIO pins
* GPIO12
* GPIO16
* GPIO17
* GPIO22
* GPIO23
* GPIO24
* GPIO25
* GPIO26
* GPIO27

#### Super weird edge cases no one but me should worry about
* If we're already running the water pump and start brewing, what should happen?
    * We should open the solenoid too
    * When brewing stops (either due to actually stopping the brew, or due to preinfusion), we stop pumping. There's no practical use case for remembering the previous pump state.
    
