# http://www.tweaking4all.com/hardware/arduino/adruino-led-strip-effects/#theatre_chase
import machine, time, neopixel, urandom

np = neopixel.NeoPixel(machine.Pin(4), 8)
numpixels = 8
dim = (25,25,25)
bright = (255,255,255)

while True:
    r = urandom.getrandbits(8)
    if r > 50:
        np[r//32] = bright
        np.write()
        time.sleep(.05)
    np.fill(dim)
    np.write()
    time.sleep(255/765)

