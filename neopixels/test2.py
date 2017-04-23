import machine, time, neopixel
machine.freq(160000000)

np = neopixel.NeoPixel(machine.Pin(4), 8)
numpixels = 8

def wheel(v):
    v *= 3
    if v < 255:
        return v, 255-v, 0
    elif v < 510:
        v -= 255
        return 255-v, 0, v
    else:
        v -= 510
        return 0, v, 255-v

j=0
while True:
    for i in range(numpixels):
        np[i] = wheel( (j+(i*5)) & 255)
    np.write()
    j += 1
    time.sleep(.005)