import machine, bh1750

# init eps8266 i2c
scl = machine.Pin(5)
sda = machine.Pin(4)
i2c = machine.I2C(scl,sda)

s = bh1750.BH1750(i2c)

while True:
    s.get_measurement(mode=s.ONCE_HIRES_2)

