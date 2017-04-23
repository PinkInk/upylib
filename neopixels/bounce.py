import machine, time, neopixel
from urandom import getrandbits

numpixels = 8
numbits = 8
np = neopixel.NeoPixel(machine.Pin(4), numpixels)

i,v = 0,-1
while True:
    if i == 0:
        colour = (getrandbits(numbits), \
                  getrandbits(numbits), \
                  getrandbits(numbits))    
    np[i] = colour
    np.write()
    time.sleep(i*.02)
    for j,p in enumerate(np):
        np[j] = (x//2 for x in p) 
    if i in (numpixels-1,0):
        v = -v
    i += v
