# Micropython bh1750 i2c digital light sensor driver

Samples ambient light level/luminance in lumens per m2 (lux).

Only tested on the esp8266 micropython port.

```python
import machine
from bh1750 import BH1750

scl = machine.Pin(5)
sda = machine.Pin(4)
i2c = machine.I2C(scl,sda)

s = BH1750(i2c)

while True:
    s.luminance(BH1750.ONCE_HIRES_1)
```

## Address

Breakout modules typically offer an **addr** pin which, if left floating or pulled to ground, configure the sensor to use its default I2C address of 0x23;

```python
s = BH1750(i2c) # addr defaults to 0x23, or;
s = BH1750(i2c, 0x23) # specify addr explicitly
```

If this address conflicts with another device on the bus **addr** pin can be pulled high and the sensor will use the alternative address 0x5c;

```python
s = BH1750(i2c, 0x5c) # use alternative i2c address
```

## Modes

**HIRES modes are recommended by the manufacturers to reduce noize (but take longer to sample).**

| constant | description |
| -------- | ----------- |
| CONT_LOWRES | Continuous, low resolution (4lx), sampling takes ~24ms, sensor remains on after reading. |
| CONT_HIRES_1 | Continuous, high resolution (1lx), sampling takes ~180ms, sensor remains on after reading. |
| CONT_HIRES_2 | Continuous, very high resolution (.5lx), sampling takes ~180ms, sensor remains on after reading. |
| ONCE_HIRES_1 | One-shot, low resolution (4lx), sampling takes ~24ms, sensor powered down after reading |
| ONCE_HIRES_2 | One-shot, high resolution (1lx), sampling takes ~180ms, sensor powered down after reading |
| ONCE_LOWRES | One-shot, very high resolution (.5lx), sampling takes ~180ms, sensor powered down after reading |
