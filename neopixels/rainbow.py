# http://www.tweaking4all.com/hardware/arduino/adruino-led-strip-effects/#theatre_chase
import machine, time, neopixel

np = neopixel.NeoPixel(machine.Pin(4), 8)
numpixels = 8

def wheel(wheelPos):
    c = [0,0,0]
    if wheelPos < 85:
        return (wheelPos*3, 255-wheelPos*3, 0)
    elif wheelPos < 170:
        wheelPos -= 85
        return (255-wheelPos*3, 0, wheelPos*3)
    else:
        wheelPos -= 170
        return (0, wheelPos*3, 255-wheelPos*3)

j = 0
while True:
    for i in range(numpixels):
        np[i] = wheel(int(((i*256/8)+j))&255)
    np.write()
    j += 1
