import machine, time, neopixel
from urandom import getrandbits

np = neopixel.NeoPixel(machine.Pin(4), 8)
black = (0,0,0)
c = [0,0,0]
v = [getrandbits(5),getrandbits(5),getrandbits(5)]

while True:
    for i,j in enumerate(c):
        if c[i]+v[i] < 0 or c[i]+v[i] > 255:
            v[i] = -v[i]
        c[i] += v[i]
    np.fill(c)
    np.write()
    time.sleep(.05)


    for i in range(12):
        if i%2 == 0:
            np.fill(c)
        else:
            np.fill(black)
        np.write()
        time.sleep(.05)
