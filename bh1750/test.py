import machine
from bh1750 import BH1750

# init eps8266 i2c
scl = machine.Pin(5)
sda = machine.Pin(4)
i2c = machine.I2C(scl,sda)

s = BH1750(i2c)

while True:
    s.luminance(BH1750.ONCE_HIRES_1)

