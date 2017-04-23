import machine, time, neopixel, urandom

np = neopixel.NeoPixel(machine.Pin(4), 8)
numpixels = 8
black = [0,0,0]
c = [0,0,0]

while True:
    for i in range(12):
        if i%2 == 0:
            np.fill(c)
        else:
            np.fill(black)
        np.write()
        time.sleep(.05)
    time.sleep(1)
    if c[0]+25 < 255:
        for i,j in enumerate(c):
            c[i] = j+50
    else:
        c = [0,0,0]
