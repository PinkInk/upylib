import machine, time, neopixel

numpixels = 8
np = neopixel.NeoPixel(machine.Pin(4), numpixels)

i = v = 1
while True:
    # np.fill((0,0,0))
    c = int((i+1)*31)
    np[i] = (c,c,c)
    np.write()
    time.sleep(i*.02)
    np[i] = (0,0,0) # quicker than fill?
    if i in (numpixels-1,0):
        v = -v
    i += v
