import machine, time, neopixel
from urandom import getrandbits
machine.freq(160000000)

numpixels = 8
numbits = 7
tail = 5 # larger == shorter tail
np = neopixel.NeoPixel(machine.Pin(4), numpixels)

i,v = 0,-1
# i1,v1 = numpixels-1,1
i1,v1 = 0,-1
delay = 5 # delay starting 2nd pixel
while True:
    if i == 0:
        colour = tuple((getrandbits(numbits) for _ in range(3)))    
    if not(delay) and i1 == 0:
        colour1 = tuple((getrandbits(numbits) for _ in range(3)))    
    np[i] = (sum(x) for x in zip(np[i], colour))
    if not(delay):
        np[i1] = (sum(x) for x in zip(np[i1], colour1))
    np.write()
    time.sleep(.1)
    for j,p in enumerate(np):
        np[j] = (x//tail for x in p) 
    if i in (numpixels-1,0):
        v = -v
    i += v
    if not(delay) and i1 in (numpixels-1,0):
        v1 = -v1
    if not(delay):
        i1 += v1
    if delay > 0:
        delay -= 1