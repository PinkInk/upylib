# upylib
My Micropyhthon libraries, for pyboard, wipy and esp8266 port, all under MIT license.

The potentially useful;

- **ublob**: micro blob class, helper for manipulating binary data on memory constrained systems, target: micropython esp8266 port (but note: micropython ga1.8 has a bug in memoryview implementation that prevents this working unless you can compile from source more recent than 7/5/16, or wait for next release binary)
- **usnmp**: micro SNMP packet/protocol library, targetting and fully functional on WiPy.  ublob above is part of initial effort to reduce footprint to enable functionality on esp8266 micropython port.


The less useful and/or outdated and/or amateur and/or just plain broken and forgotten about;

- **CharLCDPlate**: very old/immature driver for adafruit CharLCDPlate
- **dcmotor**: very old/immature driver for dual h-bridge motor-driver skin
- **nxtmotor**: very old/immature driver for lego nxt motor, and encoder reader
- **pwm**: pwm for pyboard, from the days before micropython supported pwm directly (maintained for posterity)
- **uhttpsrv**: blocking http svr


Regards, Tim

