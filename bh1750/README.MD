#Micropython bh1750 i2c digital light sensor driver

Adapted for Micropython from 
[this RPi driver](https://gist.github.com/oskar456/95c66d564c58361ecf9f),
only tested on the Micropython esp8266 port.  

Supposedly returns current ambient light lux value (lumen/m2) but please note
that I've not verified the original sources calculations against the 
manufacturers documentation, as I'm only interested in relative change.

```python
import machine, bh1750

# init eps8266 i2c
scl = machine.Pin(5)
sda = machine.Pin(4)
i2c = machine.I2C(scl,sda)

s = bh1750.BH1750(i2c)

while True:
    s.get_measurement()
```

Refer comments in source for modes and options.