import machine, time, neopixel, urandom

np = neopixel.NeoPixel(machine.Pin(4), 8)
numpixels = 8
pink = 255,20,147
red = 255,0,0
green = 0,255,0
blue = 0,0,255
purple = 148,0,211
gold = 255,215,0

while True:
    for i in range(8):
        np.fill((0,0,0))
        np[i] = red
        if i+1<8: np[i+1] = green
        if i+2<8: np[i+2] = blue
        if i+3<8: np[i+3] = purple
        if i+4<8: np[i+4] = gold
        np.write()
        time.sleep(.05)