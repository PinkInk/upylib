import machine, time, neopixel

np = neopixel.NeoPixel(machine.Pin(4), 8)
red = (255,0,0)
green = (0,255,0)
numpixels = 8

while True:
    for i in range(numpixels):
        if i%2 == 0:
            np[i] = red
        else:
            np[i] = green
    np.write()
    time.sleep(.25)
    for i in range(numpixels):
        if i%2 == 0:
            np[i] = green
        else:
            np[i] = red
    np.write()
    time.sleep(.25)

while True:
    for i in range(numpixels): 
        np.fill(green)
        np[i] = red
        np.write()
        time.sleep(.05)
