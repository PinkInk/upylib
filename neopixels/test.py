import machine, time, neopixel
from urandom import getrandbits
machine.freq(160000000)

numpixels = 8
np = neopixel.NeoPixel(machine.Pin(4), numpixels)
white = 0xff, 0xff, 0xff
black = 0x00, 0x00, 0x00
stutter = 10

while True:
    # colour = tuple((getrandbits(8) for _ in range(3)))
    for i in range(stutter):
        # np.fill(colour); np.write()
        np.fill(white); np.write()
        time.sleep((stutter-i)*.01)
        np.fill(black); np.write()
        time.sleep((stutter-i)*.01)
    for i in range(stutter,0,-1):
        # np.fill(colour); np.write()
        np.fill(white); np.write()
        time.sleep((stutter-i)*.01)
        np.fill(black); np.write()
        time.sleep((stutter-i)*.01)
    

